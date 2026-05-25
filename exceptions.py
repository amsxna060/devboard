

# NotFoundError(Exception) — takes resource and id
# ForbiddenError(Exception) — takes message
# BusinessError(Exception) — takes message and status_code

class NotFoundError(Exception):
    def __init__(self,resource,id):
        self.resource = resource
        self.id = id
        super().__init__(f"{resource} with id {id} not found") # I have called it because code suggested but don't know why we called it or we always need to call it or we can avoid this call?

class ForbiddenError(Exception):
    def __init__(self,message):
        self.message = message
        super().__init__(message)

class BusinessError(Exception):
    def __init__(self,message,status_code):
        self.message = message
        self.status_code = status_code
        super().__init__(message)