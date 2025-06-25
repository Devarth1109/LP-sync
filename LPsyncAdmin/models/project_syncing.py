from django.db import models
from LPsyncAdmin.models.usermodel import User
from LPsyncAdmin.models import Project

class ProjectSyncing(models.Model):
    choices = (
        (0, 'Magento'),
        (1, 'Shopify')
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)
    platform = models.PositiveSmallIntegerField(choices=choices, default=0)
    endpoint_url = models.CharField(max_length=255, null=True, blank=True)
    token_url = models.CharField(max_length=255, null=True, blank=True)
    admin_username = models.CharField(max_length=255, null=True, blank=True)
    admin_email = models.EmailField(null=True, blank=True)
    admin_password = models.CharField(max_length=255, null=True, blank=True)
        
    def __str__(self):
        return f"{self.user.username} - {self.project.project_name} - {self.get_platform_display()}"
