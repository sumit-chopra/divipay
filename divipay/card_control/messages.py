class Messages(object):
    class Card(object):
        CREATION_SUCCESS = "Card created successfully"
        CREATION_FAILED = "Card creation failed "
        DETAILS_NOT_FOUND = "Details for this card could not be found"
        
    class Control(object):
        CREATION_SUCCESS = "Control created successfully"
        VALIDATION_FAILED = "Not a valid control value. Please refer to validation data"
        MULTIPLE_CHECK_FAILED = "Multiple values can not exist. Either update or delete"
        INVALID_NAME= "Not a valid control name"
        FAILED_TO_COMPLY = "Failed to comply with control "
        
    class Transaction(object):
        APPROVED = "Transaction has been successfully approved"
        INSUFFICIENT_BALANCE = "Insufficient balance to carry out this transaction"
        FETCH_FAILURE = "Unable to fetch transaction "
        
    class Common(object):
        AUTHORIZATION_FAILURE = "Sorry, you are not authorized to perform this operation"
        CONNECTION_ERROR = "Connection Error"