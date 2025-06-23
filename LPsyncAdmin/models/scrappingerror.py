from django.db import models
from LPsyncAdmin.models.sitemap import Sitemap
from LPsyncAdmin.models.product import Product
from LPsyncAdmin.models.usermodel import User

class ProductWithErrors(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    sitemap = models.ForeignKey(Sitemap, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)  
    product_url = models.CharField(max_length=500, null=True, blank=True)  
    errors = models.TextField(null=True) 

    class Meta:
        db_table = "productwitherrors"

    def __str__(self):
        if self.product:
            product_str = self.product.product_url if hasattr(self.product, 'product_url') else str(self.product)
        else:
            product_str = self.product_url or "No product"
            
        sitemap_name = self.sitemap.sitemap_name if self.sitemap else "No sitemap"
        return f"{sitemap_name} - {product_str}"