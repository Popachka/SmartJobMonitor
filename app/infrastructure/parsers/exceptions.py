class ParserError(Exception):
    pass


class TooManyPagesError(ParserError):
    pass


class NotAResumeError(ParserError):
    pass
