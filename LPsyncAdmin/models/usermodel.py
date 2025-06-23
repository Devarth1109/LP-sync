from django.db import models

class User(models.Model):
    username = models.CharField(max_length=255, null=True)
    email = models.EmailField(null=True, blank=True)
    pswd = models.CharField(max_length=255, null=True)
    cpswd = models.CharField(max_length=255, null=True)

    class Meta:
        db_table = 'user'

    def __str__(self):
        return self.username