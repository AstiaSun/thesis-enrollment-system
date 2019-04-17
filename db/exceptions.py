class ObjectExistsException(Exception):
    def __init__(self, type_obj: str, object_info: dict):
        super().__init__(f'Failed to create object of type {type_obj} with '
                         f'params {object_info}. Already exists.')


class IncorrectArgumentException(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class ObjectDoesNotExist(Exception):
    def __init__(self, type_obj: str, params: dict):
        super().__init__(f'Object <{type_obj}> with fields {params} dose not '
                         f'exist in the database')
