class Borg:
    """ 共享模式一 """
    _we_are_one = {}

    def __new__(cls, *args, **kwargs):
        self = object.__new__(cls, *args, **kwargs)
        self.__dict__ = cls._we_are_one
        return self


def borg(cls):
    """ 共享模式二(装饰器版) """
    cls._state = {}
    orig_init = cls.__init__

    def new_init(self, *args, **kwargs):
        self.__dict__ = cls._state
        orig_init(self, *args, **kwargs)

    cls.__init__ = new_init
    return cls


@borg
class A:
    pass
