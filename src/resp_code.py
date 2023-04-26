
class CodeMsg(object):
    def __init__(self, msg="success", code=200, data={}) -> None:
        self.msg = msg
        self.code = code
        self.data = data

    def to_json(self, msg="", data={}):
        data = {**self.data, **data}
        return {
            "msg": msg or self.msg,
            "code": self.code,
            "data": data,
        }


class ResponseMsg(object):
    """
    Error codes
    """
    SUCCESS = CodeMsg()
    INVALID = CodeMsg("invalid", 400)
    FAIL = CodeMsg("fail", 400)
    ERROR = CodeMsg("server_error", 500)

    USER_NOT_FOUND = CodeMsg("user_not_found", 404)
    NOT_FOUND = CodeMsg("not_found", 404)
    OTP_SENT = CodeMsg("otp_sent", 200)
    OTP_EXPIRED = CodeMsg("otp_expired", 400)
    OTP_WRONG = CodeMsg("otp_wrong", 400)
    RATE_LIMIT = CodeMsg("rate_limit", 429)
    BANNED = CodeMsg("banned", 406)
    RATE_LIMIT_PURCHASE = CodeMsg("rate_limit_purchase", 400)
    FORCE_UPDATE_APP = CodeMsg("force_update", 426)
    UNAUTHORIZED = CodeMsg("unauthorized", 401)
    BLOCK = CodeMsg("block", 403)
    LOGIN_CONFLICT = CodeMsg("conflict", 409)
