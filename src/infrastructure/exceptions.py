class ParserError(Exception):
    """Базовое исключение для парсера"""
    pass

class NotAResumeError(ParserError):
    """Файл успешно обработан, но это не резюме"""
    pass

class TooManyPagesError(ParserError):
    """В файле слишком много страниц для текущей модели"""
    pass

class UserNotFoundError(Exception):
    pass

class VacancyNotFoundError(Exception):
    pass
