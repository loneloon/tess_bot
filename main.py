import sys
import os
import datetime
from core.bot import BotBase
from logger.logger import Log
from settings import *
from db_assets.db import WebsiteDB as Database
from db_assets.models import TestingSite


class TelegramBot(BotBase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.db = Database(DB_NAME, TestingSite)

        if 'Debug' not in self.__class__.__name__:
            sys.stdout = open(os.devnull, 'w')

        @self.bot.message_handler(commands=['start'])
        @Log()
        def start_response(message):
            """
            The /start command is called by default each time a user
            starts a chat with the bot, it also may be called manually by a user.

            All handler decorated functions are passed a message object as the only argument.
            Message objects contain chat id value which is used to post a reply back to the api.

            User's unique identifier is resolved by resolve_username method (see below).
            Using said identifier register_user method is initiated (see below).
            If the latter returns True, greeting is issued for the user, otherwise denied access message will
            be post.

            :param message:
            :return:
            """

            username = self.resolve_username(message)

            result = self.register_user(username)

            if result:
                self.bot.send_message(message.chat.id, "{0}{1}!".format(GREETING, username))
            else:
                self.bot.send_message(message.chat.id, ACCESS_DENIED)

        @self.bot.message_handler(commands=['test'])
        @Log()
        def initiate_test(message):
            """
            The /test command initiates test sequence or returns a specific message (provided through settings)
            if user has already tested.

            :param message:
            :return:
            """

            username = self.resolve_username(message)

            if not self.is_tested(username):
                if not self.is_test_running(username):
                    self.start_test(username)
                    self.send_next_question(username, message.chat.id)
            else:
                self.bot.send_message(message.chat.id, ALREADY_TESTED)

        @self.bot.message_handler(content_types=['text'])
        @Log()
        def resolve_message(message):
            """
            This method resolves any text messages besides assigned commands.

            If user is being tested, user input will be recorded as an answer to the current question,
            otherwise it may resolve plain text; options vary, depending on user status (super on not).

            :param message:
            :return:
            """

            username = self.resolve_username(message)
            
            if self.is_test_running(username):
                if self.is_waiting_for_user(username):
                    self.record_answer(username, message.text)

                    if self.get_current_question_id(username) is not None:
                        self.send_next_question(username, message.chat.id)
                    else:
                        self.end_test(username)
                        self.bot.send_message(message.chat.id, TEST_COMPLETE)
                        
            elif self.is_superuser(username):
                self.super_triggers(message)
            else:
                self.default_triggers(message)

    @staticmethod
    def resolve_username(message):
        """
        This method resolves what should be used as an identifier for the user: telegram username or id.

        Each one is unique for telegram, but it is more convenient to use username due to them being
        public for all telegram users, meaning - being open for user search and linking
        in messages as such @username.

        If a user hasn't set up his/her username previously, we will only be able to address them by id.

        :param message:
        :return:
        """

        if message.from_user.username is not None:
            return message.from_user.username
        else:
            return "tg://user?id=" + message.from_user.id

    def get_user_instance(self, name):
        user = self.db.get_object(model=TestingSite.User, name=name)

        return user

    def get_test_instance(self, name):
        user = self.get_user_instance(name)
        test_instance = self.db.get_object(model=TestingSite.Test, user_fk=user.id)

        return test_instance

    @Log()
    def register_user(self, name):
        """
        If user's name is included in the ban list, returns False.
        Otherwise if user is not in the database yet - creates a record of the user and
        his personal testing record. If the record can't be created or exception is raised - returns False,
        if none of the above applies (user has been found in the db) returns True.

        :param name:
        :return:
        """

        if name in BANNED_USERS:
            return False
        elif not self.db.get_object(model=TestingSite.User, name=name):
            try:
                self.db.create_object(model=TestingSite.User,
                                      name=name,
                                      is_tested=False,
                                      registration_date=datetime.datetime.now(),
                                      is_superuser=False)

                user_id = self.db.get_object(model=TestingSite.User, name=name).id

                self.db.create_object(model=TestingSite.Test,
                                      user_fk=user_id,
                                      is_running=False,
                                      is_waiting_for_input=False)
                return True
            except Exception as e:
                print(e)
                return False
        return True

    def is_superuser(self, name):
        user = self.get_user_instance(name)

        if user:
            if user.is_superuser:
                return True
        return False

    def is_tested(self, name):
        """
        Checks if user has completed the test previously. User can only be marked as tested
        after completing all the questions, reaching end_test sequence (see below).

        :param name:
        :return:
        """

        user = self.get_user_instance(name)

        if user:
            return user.is_tested
        else:
            return False

    def is_test_running(self, name):
        """
        Returns a value(bool) of a user's test record in the database.

        :param name:
        :return:
        """

        test_instance = self.get_test_instance(name)

        if test_instance:
            if test_instance.is_running:
                return True
        return False

    def waiting_io(self, name):
        """
        'Switches' the waiting parameter of a user's test record.
        If is_waiting parameter is set to True, any following user input will be
        recorded as an answer to the pending question for that user.

        :param name:
        :return:
        """

        test_instance = self.get_test_instance(name)

        if test_instance.is_waiting_for_input:
            test_instance.is_waiting_for_input = False
        else:
            test_instance.is_waiting_for_input = True

        self.db.update_object(test_instance)

    def is_waiting_for_user(self, name):
        """
        Returns the is_waiting value of a user's test record.

        :param name:
        :return:
        """

        test_instance = self.get_test_instance(name)

        if test_instance.is_waiting_for_input:
            return True
        else:
            return False

    def get_current_question_id(self, name):
        """
        Quite baldly returns the id of the next unanswered question field in
        user's test record.

        :param name:
        :return:
        """

        test_instance = self.get_test_instance(name)

        for key in QUESTIONS.keys():
            if test_instance.__getattribute__(f"question{key}") is None:
                return key
        return None

    @Log()
    def start_test(self, name):
        """
        Switches the is_running test object parameter.

        :param name:
        :return:
        """

        user = self.db.get_object(model=TestingSite.User, name=name)
        test_instance = self.db.get_object(model=TestingSite.Test, user_fk=user.id)

        test_instance.is_running = True
        self.db.update_object(test_instance)

    def send_next_question(self, name, chat_id):
        """
        Posts the next unanswered question, then switches to the waiting mode.

        !!!
        Test questions should be provided in the settings!

        Natural numbers should be used for keys,
        values should be represented by tuples of two strings (question, right_answer)
        or a string and a list of strings (question, [option1, option2, ...]).

        :param name:
        :param chat_id:
        :return:
        """

        question_id = self.get_current_question_id(name)

        if question_id is not None:
            self.bot.send_message(chat_id, QUESTIONS[question_id])
            self.waiting_io(name)

    def record_answer(self, name, answer):
        """
        Compares user input to the correct answer or searches in a list of answers,
        writes result to the database, switches waiting mode.

        :param name:
        :param answer:
        :return:
        """

        test_instance = self.get_test_instance(name)
        question_id = self.get_current_question_id(name)

        if answer.lower() in QUESTIONS[question_id][1]:
            test_instance.__setattr__("question" + str(question_id), True)
        else:
            test_instance.__setattr__("question" + str(question_id), False)

        self.db.update_object(test_instance)
        self.waiting_io(name)

    def end_test(self, name):
        """
        Sets user object to tested; for the test object - is_running is set to False.

        :param name:
        :return:
        """

        user = self.get_user_instance(name)
        test_instance = self.get_test_instance(name)

        test_instance.is_running = False
        user.is_tested = True

        self.db.update_object(test_instance)
        self.db.update_object(user)

    @Log()
    def send_invite(self, message):
        """
        Gets group invitation link through telegram api and send it to the client.

        Used blatantly at the end of the test at the moment. I would assume it should be
        issued after passing some test criteria (for instance a certain percentage of correct answers).

        !!!
        Group/channel id/name should be provided in the settings!
        Make sure that bot is an active administrator of the group with a privilege to manage users.

        :param message:
        :return:
        """

        invitation_link = self.bot.export_chat_invite_link(SECRET_GROUP)
        if invitation_link:
            self.bot.send_message(message.chat.id, invitation_link, reply_markup=None)
    
    def default_triggers(self, message):
        """
        Paste any string filters and resulting functions here if you want the bot to react to
        key phrases, words besides the test itself.

        User message string can be accessed through message.text

        :param message:
        :return:
        """

        pass
    
    def super_triggers(self, message):
        pass


class DebugBot(TelegramBot):
    """
    Launch this if you want all the logs printed out into the console!

    Otherwise launch regular. Logs will be saved to logs/log_date.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


if __name__ == "__main__":

    bot = TelegramBot(token=TOKEN)
    bot.run()
