from django.http import JsonResponse
from django.core.cache import cache
from django.db import transaction
from django.db.models import Count
import logging
from enum import Enum
from . import services_divipay
from . import errors
from .models import Card, Control, Transaction
from .group_concat import GroupConcat
from .processor_control import processControls
from .utility import create_success_response, create_fail_response
from .messages import Messages

logger = logging.getLogger(__name__)

def get_dummy_txn(request):
    txn = None
    try:
        
        # Fetch transaction details from Divipay
        txn_data = services_divipay.get_txn()
        logger.debug("Fetched transaction from divipay")
        card_id = txn_data["card"]
        txn_amount = float(txn_data["amount"])
        
        # Retrieve grouped controls from Database
        controls = retrieve_grouped_controls(card_id)
        
        # Process controls to check whether the transaction can be carried or not
        logger.info("Processing controls against the transaction object")
        processControls(txn_data, controls)
        
        with transaction.atomic():
            # Lock the database row for updating balance 
            card = Card.objects.select_for_update().get(id=card_id)
            
            # Check transaction amount against card balance
            if card.balance < txn_amount:
                raise errors.InsufficientBalanceError
            card.balance -= txn_amount
            card.save()
            logger.info("Balance updated in the database")
        txn = __create_txn_object(txn_data, TxnStatus.A)
        reply = create_success_response(Messages.Transaction.APPROVED)
        logger.info("Transaction has been approved.")
    except errors.TxnFetchError as e:
        logger.error("Transaction could not be fetched from divipay " + e.message)
        reply = create_fail_response(e.message)
    except Card.DoesNotExist:
        logger.error("Card does not exist, rejecting the transaction")
        txn = __create_txn_object(txn_data, TxnStatus.R, Messages.Card.DETAILS_NOT_FOUND)
        reply = create_fail_response(Messages.Card.DETAILS_NOT_FOUND)
    except errors.ControlException as control_exception:
        logger.error("Control exception raised " + control_exception.message)
        txn = __create_txn_object(txn_data, TxnStatus.R, control_exception.message)
        reply = create_fail_response(control_exception.message, control_exception.errors.control)
    except errors.InsufficientBalanceError as insufficient_bal_exception:
        logger.error("Insufficient balance to carry out the transaction")
        txn = __create_txn_object(txn_data, TxnStatus.R, insufficient_bal_exception.message)
        reply = create_fail_response(insufficient_bal_exception.message)
    if txn is not None:
        # Saving transaction object in the database 
        txn.save()
    return JsonResponse(reply)

def retrieve_grouped_controls(card_id):
    # Retrieve query result from cache
    # This cache is cleared whenever a new control is added / deleted for the particular card
    # Refer models.py 
    cached_controls = cache.get("group_control_" + card_id)
    if cached_controls is not None:
        return cached_controls
    else:
        # Query = select control_name, group_concat(control_value) from controls where card = card_id group by control_name
        cached_controls = Control.objects.filter(card=card_id).values('control_name').annotate(count=Count('control_name'), control_value_list=GroupConcat('control_value'))
        grouped_control_dict = dict()
        for control in cached_controls:
            grouped_control_dict[control["control_name"]] = control["control_value_list"]
        cache.set("group_control_" + card_id, grouped_control_dict)
        return grouped_control_dict    

class TxnStatus(Enum):
    A = 0
    R = 1

def __create_txn_object(txn_data, txn_status, reason = None):
    txn = Transaction(id=txn_data["id"],
                      card=txn_data["card"],
                      amount=txn_data["amount"],
                      merchant=txn_data["merchant"], 
                      merchant_category=txn_data["merchant_category"],
                      created_at=txn_data["created"], 
                      updated_at=txn_data["updated"],
                      status=txn_status.name, 
                      reason=reason
            )
    return txn