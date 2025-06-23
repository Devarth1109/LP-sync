from django.contrib import admin
from LPsyncAdmin.models import Product, Sitemap, Project, ProductWithErrors, ProjectSyncing
from LPsyncAdmin.models.usermodel import User

# Register your models here.
admin.site.register(User)
admin.site.register(Project)
admin.site.register(Sitemap)
admin.site.register(Product)
admin.site.register(ProductWithErrors)
admin.site.register(ProjectSyncing)