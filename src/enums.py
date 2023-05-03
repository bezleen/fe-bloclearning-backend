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
    THIRD_PARTY = "third_party"


class Avatar(EnumBase):
    AVATAR_1 = "static/avatar_1.webp"
    AVATAR_2 = "static/avatar_2.webp"
    AVATAR_3 = "static/avatar_3.webp"
    AVATAR_4 = "static/avatar_4.webp"
