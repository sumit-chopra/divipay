from django.urls import path
  
from . import views_control, views_card
from card_control import views_txn


urlpatterns = [
        path('stub/card', views_card.create_card.as_view(), name='Create stub Card'),
        path('stub/txn', views_txn.get_dummy_txn, name='Process stub transaction'),  
        path('api/v1/card/<str:card_id>/control', views_control.get_post_controls.as_view(), name='getPostControls'),
        path('api/v1/card/<str:card_id>/control/<int:pk>', views_control.delete_controls.as_view(), name='deleteControl'),
]