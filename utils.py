import re
import hashlib

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
