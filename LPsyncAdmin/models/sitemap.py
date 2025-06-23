from django.db import models
from LPsyncAdmin.models.usermodel import User
from LPsyncAdmin.models.project import Project  # <-- Add this import


class Sitemap(models.Model):
	url = models.CharField(max_length=200)
	sitemap_name = models.CharField(max_length=200)
	category = models.CharField(max_length=200)
	project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True)  # <-- Add this line
	user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

	class Meta:
		db_table = "sitemap"
		# app_label = 'django_adminlte'
		
	def __str__(self):
		return self.sitemap_name