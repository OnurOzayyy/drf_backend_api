from django.db import models
from django.conf import settings
from django.db.models.signals import pre_save, post_save
from carts.models import Cart
from decimal import Decimal
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
        """
        If the user does not have braintree id, create a new customer
        save the customer id as the braintree id for the user.  
        """
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
        """
        if the user has a customer id in braintree, 
        generate a client token. Save and return the client token. 
        """
        customer_id = self.get_braintree_id
        if customer_id:
            client_token = gateway.client_token.generate({
                "customer_id": customer_id
            })
            return client_token
        return None

def update_braintree_id(sender, instance, *args, **kwargs):
    """
    if the user does not have a braintree id, create one. 
    """
    if not instance.braintree_id:
        instance.get_braintree_id

post_save.connect(update_braintree_id, sender=UserCheckout)
                
ADDRESS_TYPE = (
    ('billing', 'BILLING'),
    ('shipping', 'SHIPPING')
)

class UserAddress(models.Model):
    """
    User Address Model. 
    """
    user = models.ForeignKey(UserCheckout, on_delete=models.CASCADE)
    type = models.CharField(max_length=120, choices=ADDRESS_TYPE)
    street = models.CharField(max_length=120)
    city = models.CharField(max_length=120)
    state = models.CharField(max_length=120)
    zipcode = models.CharField(max_length=120)

    def __str__(self):
        return self.street
    
    def get_address(self):
        return f'{self.street} {city} {state} {zipcode}'


ORDER_STATUS_CHOICES = (
    ('created', 'Created'),
    ('paid', 'Paid'),
    ('shipped', 'Shipped'),
    ('refunded', 'Refunded')
)

class Order(models.Model):
    """
    Order Model. 
    """
    status = models.CharField(max_length=120, choices=ORDER_STATUS_CHOICES, default='created')
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    user = models.ForeignKey(UserCheckout, null=True, on_delete=models.CASCADE)
    billing_address = models.ForeignKey(UserAddress, related_name='billing_address', null=True, on_delete=models.CASCADE)
    shipping_address = models.ForeignKey(UserAddress, related_name='shipping_address', null=True, on_delete=models.CASCADE)
    shipping_total_price = models.DecimalField(max_digits=20, null=True, blank=True, decimal_places=2, default=10)
    order_total = models.DecimalField(max_digits=20, decimal_places=2)
    order_id = models.CharField(max_length=20, null=True, blank=True)

    def __str__(self):
        return f'Order_id: {self.id}, Cart_id:{self.cart.id}'
    
    class Meta: 
        ordering = ['-id']

    def get_absolute_url(self):
        return reverse('order_detail', kwargs={"pk": self.pk})

    def mark_completed(self, order_id=None):
        self.status = 'paid'
        if order_id and not self.order_id:
            self.order_id = order_id
            self.save()
    @property
    def is_complete(self):
        if self.status == 'paid':
            return True
        return False

def order_pre_save(sender, instance, *args, **kwargs):
    shipping_total_price = instance.shipping_total_price
    cart_total = instance.cart.total
    order_total = Decimal(shipping_total_price) + Decimal(cart_total)
    instance.order_total = order_total

pre_save.connect(order_pre_save, sender=Order)
