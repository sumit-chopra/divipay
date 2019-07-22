from django.db import models
from django.conf import settings
from django.core.cache import cache

class Card(models.Model):
    id = models.CharField(max_length=40, primary_key=True)
    user = models.IntegerField()
    balance = models.FloatField(default=0.0)
    created = models.DateTimeField()
    updated = models.DateTimeField()
    creator = models.ForeignKey('auth.User', related_name='cards', on_delete=models.CASCADE)
    
    CACHE_KEY_PREFIX = "card_"

    # overridden to cache card details
    def save(self, *args, **kwargs):
        models.Model.save(self, *args, **kwargs)
        cache.set(Card.CACHE_KEY_PREFIX + self.id, self)

    # function to return card from cache if exists otherwise from DB
    def get(card_id):
        cache_result = cache.get(Card.CACHE_KEY_PREFIX + card_id)
        if cache_result is None:
            cache_result = Card.objects.get(id=card_id)
            cache.set(Card.CACHE_KEY_PREFIX + card_id, cache_result)
        return cache_result
    
    def delete_cache(card_id):
        cache.delete(Card.CACHE_KEY_PREFIX + card_id)

    def __str__(self):
            return '{0} {1} {2}'.format(self.id, self.user_id, self.balance)
        
    get = staticmethod(get)
    delete_cache = staticmethod(delete_cache)

class Control(models.Model):
    card = models.ForeignKey(Card, on_delete=models.CASCADE)
    control_name = models.CharField(max_length=10, choices = settings.CONTROL_MODEL_NAME_CHOICES)
    control_value = models.CharField(max_length=40)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    CACHE_KEY_PREFIX = "group_control_"
    
    # overridden to delete cache for grouped controls
    def save(self, *args, **kwargs):
        models.Model.save(self, *args, **kwargs)
        cache.delete(Control.CACHE_KEY_PREFIX + self.card.id)
    
    # overridden to delete cache for grouped controls    
    def delete(self):
        cache.delete(Control.CACHE_KEY_PREFIX + self.card.id)
        return models.Model.delete(self)
    
    def __str__(self):
        return '{0} {1}'.format(self.control_name, self.control_value)
        
TXN_STATUS_CHOICES = [
        ('A', 'Approved'),
        ('R', 'Rejected')
]
            
class Transaction(models.Model):
    card = models.CharField(max_length=40)
    id = models.CharField(max_length=40, primary_key=True)
    amount = models.FloatField(default=0.0)
    merchant = models.CharField(max_length=40)
    merchant_category = models.CharField(max_length=10)
    status = models.CharField(max_length=1, choices=TXN_STATUS_CHOICES)
    reason = models.CharField(max_length = 100, null=True)
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()