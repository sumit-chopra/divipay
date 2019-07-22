from .messages import Messages

class Error(Exception):
    pass

class Unavailable(Error):
    def __init__(self):
        self.message = Messages.Common.CONNECTION_ERROR

class DiviPayError(Error):
    def __init__(self, code, message):
        self.code = code
        self.message = message
  
class InsufficientBalanceError(Error):
    def __init__(self):
        self.message = Messages.Transaction.INSUFFICIENT_BALANCE
              
class CardCreationError(Error):
    def __init__(self, message):
        self.message = message

class TxnFetchError(Error):
    def __init__(self, message):
        self.message = Messages.Transaction.FETCH_FAILURE + message
        
class ControlException(Exception):
    def __init__(self, message, errors = None):
        super().__init__(message)
        self.errors = errors
        self.message = message
                
class InvalidControlName(ControlException):
    pass

class InvalidControlValue(ControlException):
    def __init__(self, message, errors = None):
        super().__init__(message, errors)
                
class ControlExceptionPayload:
        def __init__(self, control):
                self.control = control

        def as_json(self):
                content = {
                        "failedValidation" : self.control
                }
                return content

        def __str__(self):
                return "Validation failed for control id : " + self.control["control_name"]