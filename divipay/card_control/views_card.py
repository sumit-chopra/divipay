from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
import logging
from . import services_divipay
from .serializers import CardSerializer
from .utility import create_success_response, create_fail_response
from . import errors
from .messages import Messages

logger = logging.getLogger(__name__)

class create_card(CreateAPIView):
    
    serializer_class = CardSerializer
    permission_classes = (IsAuthenticated, )
    
    def post(self, request):
        try:
            logger.info("Creating card at divipay")
            # Hitting DiviPay API to create card
            card_data = services_divipay.create_card()
            serializer = CardSerializer(data = card_data)
            if serializer.is_valid(raise_exception = True):
                serializer.save(creator=request.user)
            logger.info("Card details saved in DB")
            content = create_success_response(Messages.Card.CREATION_SUCCESS, card_data)
            status_code = status.HTTP_201_CREATED
        except errors.CardCreationError as e:
            logger.error("Card creation failed " + e.message)
            content = create_fail_response(e.message)
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        
        return Response(content, status = status_code)