import enum


class EnumBase(enum.Enum):
    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))

    @classmethod
    def list_name(cls):
        return list(map(lambda c: c.name, cls))


class Example(EnumBase):
    EXAMPLE1 = "example1"
    EXAMPLE2 = "example2"


class UserRole(EnumBase):
    DAO_MEMBER = "dao_member"
    RESEARCHER = "researcher"
