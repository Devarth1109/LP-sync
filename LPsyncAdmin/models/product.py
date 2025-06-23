from django.db import models
from LPsyncAdmin.models import Sitemap
from LPsyncAdmin.models.usermodel import User

# Create your models here.
class Product(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    sitemap = models.ForeignKey(Sitemap, on_delete=models.CASCADE, null=True)
    sku = models.CharField(max_length=100)
    linenplus_sku = models.CharField(max_length=100, null=True)
    store_view_code = models.CharField(max_length=100, null=True)
    attribute_set_code = models.CharField(max_length=100, null=True)
    categories = models.CharField(max_length=100, null=True)
    manufacturer_no = models.CharField(max_length=100, null=True)
    name = models.CharField(max_length=500, null=True)
    product_price = models.DecimalField(max_digits=8, decimal_places=2)
    linenplus_price = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    flag = models.CharField(max_length=50, default='-')
    brand = models.CharField(max_length=50, null=True)
    visibility = models.CharField(max_length=100, null=True)
    product_type = models.CharField(max_length=100, null=True)
    variation_data = models.JSONField(null=True, blank=True)
    configurable_variation_labels = models.CharField(max_length=500, null=True)
    configurable_variations = models.CharField(max_length=2000, null=True)
    product_description = models.TextField()
    stock = models.CharField(max_length=255, null=True)
    product_websites = models.CharField(max_length=255, null=True)
    msrp_display_actual_price_type = models.CharField(max_length=100, null=True)
    uom = models.CharField(max_length=50)
    cost = models.CharField(max_length=255, null=True)
    vendor_cost = models.CharField(max_length=255, null=True)
    taxes_id = models.CharField(max_length=255, null=True)
    account_number = models.CharField(max_length=255, null=True)
    delivery_text = models.CharField(max_length=255, null=True)
    property_account_income_id = models.CharField(max_length=255, null=True)
    property_account_expense_id = models.CharField(max_length=255, null=True)
    meta_title = models.CharField(max_length=255, null=True)
    meta_keywords = models.CharField(max_length=255, null=True)
    meta_description = models.CharField(max_length=255, null=True)
    type_erp = models.CharField(max_length=255, null=True)
    base_product_image = models.CharField(max_length=255, null=True)
    base_image_label = models.CharField(max_length=255, null=True)
    small_image = models.CharField(max_length=255, null=True)
    small_image_label = models.CharField(max_length=255, null=True)
    thumbnail_image = models.CharField(max_length=255, null=True)
    thumbnail_image_label = models.CharField(max_length=255, null=True)
    additional_images = models.TextField()
    additional_images_label = models.CharField(max_length=255, null=True)
    product_url = models.CharField(max_length=500, null=True)

    class Meta:
        db_table = "product"
        unique_together = ('user', 'sku', 'linenplus_sku')
        
    def __str__(self):
        return self.sku + " - " + self.linenplus_sku