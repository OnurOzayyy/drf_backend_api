from django.db import models

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
    default = models.ForeignKey("Category", related_name='default_category', null=True, blank=True, on_delete=models.CASCADE)

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


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/')

    def __str__(self):
        return self.product.title

class Category(models.Model):
    title = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(null=True, blank=True)
    active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)

    def __str__(self):
        return self.title


    def get_absolute_url(self):
        return reverse("category_detail", kwargs={"slug": self.slug})
