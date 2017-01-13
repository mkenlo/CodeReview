import re
import hashlib
import requests

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
    message = """Hello,<br>
		Welcome to CodeReview! We are building a community of good coders.
		Happy Coding!
		<br>
		CodeReview Team"""
    send_message(adrTo, subject, message)
