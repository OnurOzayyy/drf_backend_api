from django.db import models

class UserCheckout(models.Model):
    """ 
    UserCheckout Model
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.email
