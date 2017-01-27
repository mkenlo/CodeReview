import re
import hashlib
import requests
from math import ceil

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASS_RE = re.compile(r"^.{3,20}$")
EMAIL_RE = re.compile(r'^[\S]+@[\S]+\.[\S]+$')

SALT = "fthuybnkjGTFSANL124587UIJKMJKwerrt"


def valid_username(username):
    return username and USER_RE.match(username)


def valid_password(password):
    return password and PASS_RE.match(password)


def valid_email(email):
    return not email or EMAIL_RE.match(email)


def check_secure_pass(tochecked_val, secure_val):
    hash_passwd = hashlib.md5(SALT + tochecked_val).hexdigest()
    return hash_passwd == secure_val


def secure_password(password):
    return hashlib.md5(SALT + password).hexdigest()


def send_message(adrTo, subject, message):
    return requests.post(
        "https://api.mailgun.net/v3/sandboxb0c3d7e7f125401f81a6ff64c93d9e44.mailgun.org/messages",
        auth=("api", "key-9fcd8f9679b6a4522f9103bc9331a818"),
        data={"from": "Code Review <support@codereview.com>",
              "to": adrTo,
              "subject": subject,
              "text": message})


def send_welcome(adrTo):
    subject = "Welcome to CodeReview"
    message = """Hello,
		Welcome to CodeReview! We are building a community of good coders.
		Happy Coding!
		
		CodeReview Team"""
    send_message(adrTo, subject, message)


class Pagination(object):

    def __init__(self, page, per_page, total_count):
        self.page = page
        self.per_page = per_page
        self.total_count = total_count

    @property
    def pages(self):
        return int(ceil(self.total_count / float(self.per_page)))

    @property
    def has_prev(self):
        return self.page > 1

    @property
    def has_next(self):
        return self.page < self.pages

    def iter_pages(self, left_edge=2, left_current=2,
                   right_current=5, right_edge=2):
        last = 0
        for num in xrange(1, self.pages + 1):
            if num <= left_edge or \
               (num > self.page - left_current - 1 and
                num < self.page + right_current) or \
               num > self.pages - right_edge:
                if last + 1 != num:
                    yield None
                yield num
                last = num



