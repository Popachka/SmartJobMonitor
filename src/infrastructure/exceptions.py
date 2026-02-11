class ParserError(Exception):
                                        
    pass

class NotAResumeError(ParserError):
                                                  
    pass

class TooManyPagesError(ParserError):
                                                          
    pass

class UserNotFoundError(Exception):
    pass

class VacancyNotFoundError(Exception):
    pass
