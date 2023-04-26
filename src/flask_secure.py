import hashlib
from flask import Flask


def md5(str2hash):
    result = hashlib.md5(str2hash.encode())
    return result.hexdigest()


class SecureFlask(Flask):

    def __init__(self, *args, md5_endpoints=[], **kwargs):
        self.md5_endpoints = md5_endpoints
        super().__init__(*args, **kwargs)

    def add_url_rule(self, rule: str, endpoint=None, view_func=None, **options):
        if rule in self.md5_endpoints:
            md5_rule = rule
            if md5_rule.startswith("/"):
                md5_rule = md5_rule[1:]
            md5_rule = "/" + md5(md5_rule)
            print(rule, " | ", md5_rule)
            super(SecureFlask, self).add_url_rule(md5_rule, endpoint, view_func, **options)

        return super(SecureFlask, self).add_url_rule(rule, endpoint, view_func, **options)
