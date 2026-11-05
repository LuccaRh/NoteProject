# Code
class WrongLogin(Exception):
    """
    No user has this email and password
    """


class NoSession(Exception):
    """
    The request has no session cookie, or its session ended or never was
    """
