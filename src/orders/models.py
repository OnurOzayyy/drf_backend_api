from django.db import models
from django.conf import settings
from django.db.models.signals import pre_save, post_save

import braintree

gateway = braintree.BraintreeGateway(
    braintree.Configuration(
        braintree.Environment.Sandbox,
        merchant_id="mhkyv773ffmdqm5n",
        public_key="kc9cp723jkxvfk6p",
        private_key="2e1f06c7bdb5fea67ac81fe05439e173"
    )
)
class UserCheckout(models.Model):
    """ 
    UserCheckout Model
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE)
    email = models.EmailField(unique=True)
    braintree_id = models.CharField(max_length=120, null=True, blank=True)

    def __str__(self):
        return self.email
    
    @property
    def get_braintree_id(self):
        instance = self
        if not instance.braintree_id:
            result = gateway.customer.create({
                "email": instance.email,
            })
            if result.is_success:
                instance.braintree_id = result.customer.id
                instance.save()
        return instance.braintree_id

    def get_client_token(self):
        customer_id = self.get_braintree_id
        if customer_id:
            client_token = gateway.client_token.generate({
                "customer_id": customer_id
            })
            return client_token
        return None

def update_braintree_id(sender, instance, *args, **kwargs):
    if not instance.braintree_id:
        instance.get_braintree_id

post_save.connect(update_braintree_id, sender=UserCheckout)
                
