from telebot import TeleBot as Bot
from threading import Timer, Thread


class BotBase:

    def __init__(self, token: str):

        self._token = token
        self.until_timeout = 60
        self.is_running = False

        self.bot = Bot(token=token, threaded=False)

        self.main_thread = Thread(target=self.mainloop)
        self.timer = None

    def run(self):
        """
        Starts mainloop thread.

        :return:
        """

        if not self.is_running:
            self.is_running = True
            self.main_thread.start()

        else:
            print('Bot instance is already running...')

    def mainloop(self):
        """
        While is_running initiates a 60 second timer, starts polling,
        stops polling when timer runs out.

        This switch on/off allows to pass telegrams non-stop polling restrictions.
        :return:
        """

        while self.is_running:
            self.timer = Timer(self.until_timeout, self.timeout)
            self.timer.start()
            try:
                self.bot.polling()
            except Exception or KeyboardInterrupt as e:
                print(e)
                raise SystemExit

    def timeout(self):
        try:
            self.bot.stop_polling()
        except Exception as e:
            print(e)

    def terminate(self):
        self.is_running = False
        self.timer.cancel()
        self.timeout()


class EchoBot(BotBase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)

        @self.bot.message_handler(commands=["start"])
        def start_response(message):
            self.bot.send_message(message.chat.id, "Hello, i'm an echo-bot!")

        @self.bot.message_handler(content_types=["text"])
        def start_response(message):
            self.bot.send_message(message.chat.id, message.text)