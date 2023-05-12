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
    REVIEWER = "reviewer"
    THIRD_PARTY = "third_party"
    ADMIN = "admin"


class Avatar(EnumBase):
    AVATAR_1 = "static/avatar_1.webp"
    AVATAR_2 = "static/avatar_2.webp"
    AVATAR_3 = "static/avatar_3.webp"
    AVATAR_4 = "static/avatar_4.webp"


class FormType(EnumBase):
    OFFER_RESEARCHER = "offer_researcher"
    OFFER_REVIEWER = "offer_reviewer"
    OFFER_THIRD_PARTY = "offer_third_party"


class FormStatus(EnumBase):
    PENDING = "pending"
    UNPUBLISHED = "unpublished"
    DONE = "done"
    REJECTED = "rejected"


class CardIdSide(EnumBase):
    FRONT = "front"
    BACK = "back"


class ProjectStage(EnumBase):
    UNPUBLISHED = "unpublished"
    PENDING = "pending"
    REJECTED = "rejected"
    PRE_QUALIFICATION = "pre_qualified"
    REVIEWING = "reviewing"
    FUNDING = "funding"
    EXECUTING = "executing"
    COMPLETED = "completed"


class ExecutingStatus(EnumBase):
    EARLY = "early"
    TESTING = "testing"
    ALMOST_DONE = "almost_done"


class CompleteStatus(EnumBase):
    CLAIMABLE = "claimable"
    UNCLAIMABLE = "unclaimable"
    PENDING = "pending"


class FormCandidateType(EnumBase):
    ORGANIZATION = "organization",
    PERSONAL = "personal",
