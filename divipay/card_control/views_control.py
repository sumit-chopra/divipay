from django.conf import settings
from django.http.response import Http404
from rest_framework.generics import ListCreateAPIView, DestroyAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
import logging
from .serializers import ControlSerializer
from .models import Card, Control
from .processor_control import ControlProcessor
from . import errors
from .utility import create_success_response, create_fail_response
from .messages import Messages

logger = logging.getLogger(__name__)

class get_post_controls(ListCreateAPIView):
    
    serializer_class = ControlSerializer
    permission_classes = (IsAuthenticated, )
    
    def get_queryset(self):
        
        # card_id is received as part of the URL. Please see urls.py
        card_id = self.kwargs['card_id']
        logger.debug("Card id received in the request " + card_id)
        
        try:
            # Retrieve card object from database to see if card exists or not 
            Card.get(card_id)
            
            # Retrieve controls from database
            controls = Control.objects.filter(card=card_id)
            logger.info("Controls returned for the card")
        except Card.DoesNotExist:
            # card does not exist in the database, return with 404
            logger.error("Card details could not be found")
            raise Http404
        return controls
        

    def post(self, request, card_id):
        # card_id is received as part of the url. Please see urls.py
        logger.debug("Card id received in the request " + card_id)
        
        # control_name and control_value is received as JSON body of the request
        data = request.data.copy()
        data["control_name"] = data["control_name"].upper()
        data["card_id"] = card_id
        
        serializer = ControlSerializer(data=data)
        serializer.is_valid(raise_exception = True)
        
        control_name = data["control_name"]
        control_value = data["control_value"]
        try:
            # Retrieve card object from database to see if card exists or not
            card = Card.get(card_id)
            # User who has created the card can only create controls. No other user is allowed.
            if card.creator == request.user:
                # Validate the control_name and control_value
                if self.validate_control(control_name, control_value, card_id):
                    logger.info("Control has been successfully validated")
                    # add Control to database
                    serializer.save()
                    logger.info("Control object saved to database")
                    content = create_success_response(Messages.Control.CREATION_SUCCESS, serializer.data)
                    status_code = status.HTTP_201_CREATED
            else:
                content = create_fail_response(Messages.Common.AUTHORIZATION_FAILURE)
                status_code = status.HTTP_403_FORBIDDEN
        except Card.DoesNotExist:
            # card does not exist in the database, return with 404
            logger.error("Card details could not be found")
            content = create_fail_response(Messages.Card.DETAILS_NOT_FOUND)
            status_code = status.HTTP_404_NOT_FOUND
        except errors.ControlException as control_exception:
            # control validation failed
            logger.error("Control validation failed")
            content = create_fail_response(control_exception.message, control_exception.errors)
            #content["validation"] = control_exception.errors
            status_code = status.HTTP_400_BAD_REQUEST
        return Response(content, status = status_code)
        
        
    def validate_control(self, control_name, control_value, card_id):
        # Retrieve control definitions from settings.py
        # see if control with the given name is defined in definition or not
        if control_name not in settings.CONTROL_DEFINITION:
            # control_name is not a valid name for the control. Raise error
            logger.error(control_name + " does not exist in the definition")
            raise errors.InvalidControlName(Messages.Control.INVALID_NAME)
        
        # Retrieve the control definition for the given control_name
        control_def = settings.CONTROL_DEFINITION[control_name]
        
        # validate the value of control against the definition
        if ControlProcessor.factory(control_def).validate(control_value):
            logger.info("control value is validated.")
            
            # check if multiple values are allowed for this control
            if self.check_if_multiple_allowed(control_def, control_name, card_id) == False:
                logger.error("Multiple validation check failed. Raising error.")
                raise  errors.InvalidControlValue(Messages.Control.MULTIPLE_CHECK_FAILED)
            else:
                logger.info("Multiple validation check passed.")
        else:
            logger.error("control value validation failed. Raising error.")
            raise errors.InvalidControlValue(Messages.Control.VALIDATION_FAILED, control_def["input_validation"])
        return True
    
    def check_if_multiple_allowed(self, control_def, control_name, card_id):
        if "input_validation" not in control_def or "can_multiple_exists" not in control_def["input_validation"] or not control_def["input_validation"]["can_multiple_exists"]:
            # Fetch the count of controls exist for the given card id and control name
            count = Control.objects.filter(card_id=card_id).filter(control_name=control_name).count()
            if count == 0:
                logger.info("multiple not allowed. No previous entry exists in database")
                return True
            else:
                logger.info("multiple not allowed. Previous entry exists in database")
                return False
        else:
            return True
                    
    
    
# Class to implement HTTP DELETE method for control
class delete_controls(DestroyAPIView):
    serializer_class = ControlSerializer
    permission_classes = (IsAuthenticated,)
    
    def get_queryset(self, pk):
        return Control.objects.get(pk=pk)

    def delete(self, request, card_id, pk):
        try:
            control = self.get_queryset(pk)
            
            # check if card_id received in the request is same as that in the database and the user who has created the card / control is only trying to delete
            if control.card_id == card_id and control.card.creator == request.user:
                control.delete()
                content = None
                status_code = status.HTTP_204_NO_CONTENT
            else:
                content = create_fail_response(Messages.Common.AUTHORIZATION_FAILURE)
                status_code = status.HTTP_403_FORBIDDEN
        except Control.DoesNotExist:
            logger.error("Control does not exist")
            content = create_fail_response(Messages.Card.DETAILS_NOT_FOUND)
            status_code = status.HTTP_404_NOT_FOUND
        
        return Response(content, status = status_code)

