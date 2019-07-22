from django.conf import settings
import logging
from . import services
from . import errors
from .messages import Messages

logger = logging.getLogger(__name__)
headers = {
    "Authorization" : "Token " + settings.DIVIPAY_KEY
}
    
def create_card():   
    card_url = settings.DIVIPAY_API_BASE_URL + 'cards/'
    try:
        logger.info("Creating a dummy card")
        r = services.post_service(card_url, headers)
        logger.info("Card created. Response {0}".format(r["content"]))
        return r["content"]
    except (errors.Unavailable, errors.DiviPayError) as e:
        raise errors.CardCreationError(Messages.Card.CREATION_FAILED + e.message) from e
    
def get_txn():
    txn_url = settings.DIVIPAY_API_BASE_URL + 'transaction/'
    try:
        logger.info("Getting a dummy transaction")
        r = services.get_service(txn_url, headers)
        logger.info("Transaction received {0}".format(r["content"]))
        return r["content"]
    except (errors.Unavailable, errors.DiviPayError) as e:
        raise errors.TxnFetchError(e.message) from e