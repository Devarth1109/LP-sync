from django.db import models
from LPsyncAdmin.models.usermodel import User

# Create your models here.
class Project(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    project_name = models.CharField(max_length=50)
    price_margin = models.CharField(max_length=20)
    uom = models.CharField(max_length=20)
    account_number = models.CharField(max_length=50)
    type_erp = models.CharField(max_length=50)
    taxes_id = models.BigIntegerField()
    property_account_income_id = models.BigIntegerField()
    property_account_expense_id = models.BigIntegerField()
    attribute_set_code = models.CharField(max_length=50)
    product_website = models.CharField(max_length=200)
    meta_title_suffix = models.CharField(max_length=200)
    meta_description_suffix = models.CharField(max_length=200)
    status = models.PositiveSmallIntegerField(default=0)
    sitemap_json = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "project"
        
    def __str__(self):
        return self.project_name