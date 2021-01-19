import copy


class PrototypeMixin:

    def clone(self):
        return copy.deepcopy(self)


class ModelMixin:

    def get_attrs(self):
        return dict((key, self.__getattribute__(key)) for key in self.__slots__ if self.__getattribute__(key) is not None)

    @classmethod
    def init_and_get_attrs(cls, *args, **kwargs):
        return cls(*args, **kwargs).get_attrs()