from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class Role(models.Model):
    id_role = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['id_role']
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'

class CustomUser(AbstractUser):
    # username, password, first_name, last_name, etc. are already here
    email = models.EmailField(unique=True)
    phone      = models.CharField(max_length=15, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    document   = models.CharField(max_length=50, blank=True, null=True)
    role       = models.ForeignKey(Role,
                                   on_delete=models.CASCADE,
                                   related_name='users')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username

    class Meta:
        ordering = ["id"]
        verbose_name = "User"
        verbose_name_plural = "Users"

class Address(models.Model):
    id_address = models.AutoField(primary_key=True)
    street = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    neighborhood = models.CharField(max_length=50, blank=True, null=True)
    number = models.CharField(max_length=10, blank=True, null=True)
    postal_code = models.CharField(max_length=20)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.street

    class Meta:
        ordering = ['id_address']
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses'