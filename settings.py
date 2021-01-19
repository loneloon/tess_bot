
SECRET_GROUP = '*'

TOKEN = "*"

GREETING = 'Hello, '  # username is appended after

DB_NAME = 'sqlite:///test_bot_db.db3'


# Please do not deviate from the format, when updating questions.
#
# Natural numbers should be used for keys,
#         values should be represented by tuples of two strings
#         (question, right_answer) or a string and a list of strings (question, [option1, option2, ...]).

QUESTIONS = {
    1: ("Is 5 more than 3?", "yes"),
    2: ("Is 7 a prime number?", "yes"),
    3: ("Am i actually useful?", "yes")
}

ALREADY_TESTED = 'You have already tested!'
ACCESS_DENIED = 'Access denied. Bye!'
TEST_COMPLETE = 'You have completed the test!'

BANNED_USERS = []
