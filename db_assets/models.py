import datetime
from patterns.prototypes import ModelMixin
from settings import QUESTIONS


class TestingSite:
    """
    These classes are used by the db module to create tables and mapped objects.
    Use __slots__ to list all the necessary columns for each table.

    The type of stored value is defined by the name clues:

    If key name is exactly 'id', future column will be set to primary key.

    If key name contains 'email' or 'cookie', column will be set to unique string.

    If key name contains 'parent', column type will be set to int and its values will correspond
    with parents ids in the same table (0 = no parent).

    If key contains 'is_', column type will be set to Boolean.

    If key contains 'date' - datetime column.

    If key contains fk, the column will reference foreign key - id of the table
    which is specified earlier in the name. For example "user_fk" will reference User.id
    (name of the table is capitalized).

    """

    class User(ModelMixin):
        __slots__ = 'id', 'name', 'registration_date', 'is_superuser', 'is_tested'

        def __init__(self, name):
            self.id = None
            self.name = name
            self.is_tested = False
            self.registration_date = datetime.datetime.now()
            self.is_superuser = False

    class Test(ModelMixin):
        __slots__ = 'id', "user_fk", \
                    'is_running', \
                    'is_waiting_for_input', \
                    *list("question" + str(k) for k in QUESTIONS.keys())

    @classmethod
    def get_inner_classes(cls):
        return [cls_attribute for cls_attribute in cls.__dict__.values() if type(cls_attribute) is type]