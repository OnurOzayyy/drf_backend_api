"""
Product Models.
"""
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

class ProductQuerySet(models.query.QuerySet):
    """
    Query Set for the Product.
    """
    def active(self):
        """
        Active method to filter the query for active products.
        """
        return self.filter(active=True)

class ProductManager(models.Manager):
    """
    Model Manager for Product.
    """
    def get_queryset(self):
        """
        Default query set.
        """
        return ProductQuerySet(self.model, using=self._db)

    def all(self, *args, **kwargs):
        """
        Modify the all() method to return only active products.
        """
        return self.get_queryset().active()

class Product(models.Model):
    """
    Product model.
    """
    title = models.CharField(max_length=120)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(decimal_places=2, max_digits=20)
    active = models.BooleanField(default=True)
    categories = models.ManyToManyField("Category", blank=True)
    default = models.ForeignKey("Category", related_name='default_category',
                                null=True, blank=True, on_delete=models.CASCADE)

    objects = ProductManager()

    class Meta:
        """
        Ordered by title.
        """
        ordering = ["-title"]

    def __str__(self):
        """
        Return human readable representation of the model.
        """
        return self.title

    def get_absolute_url(self):
        """
        Method to tell Django how to calculate the canonical URL for an object.
        """
        return reverse('product_detail', kwargs={'pk': self.pk})

def image_upload_to(instance, filename):
    """
    Returns the path to upload an image.
    """
    title = instance.product.title
    slug = slugify(title)
    basename, file_extension = filename.split(".")
    new_filename = "%s-%s.%s" %(slug, instance.id, file_extension)
    return "products/%s/%s" %(slug, new_filename)

class ProductImage(models.Model):
    """
    Product Image class.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=image_upload_to)

    def __str__(self):
        """
        Return product title in string form.
        """
        return self.product.title

class Variation(models.Model):
    """
    Variation of a product.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    title = models.CharField(max_length=120)
    price = models.DecimalField(decimal_places=2, max_digits=20)
    sale_price = models.DecimalField(decimal_places=2, max_digits=20, null=True, blank=True)
    active = models.BooleanField(default=True)
    inventory = models.IntegerField(null=True, blank=True) #refer none == unlimited amount

    def __str__(self):
        """
        Return human readable title.
        """
        return self.title

class Category(models.Model):
    """
    Category class.
    """
    title = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(null=True, blank=True)
    active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)

    def __str__(self):
        """
        Return human readable title.
        """
        return self.title

    def get_absolute_url(self):
        """
        Returns a string that can be used to refer to the object over HTTP.
        """
        return reverse("category_detail", kwargs={"slug": self.slug})
