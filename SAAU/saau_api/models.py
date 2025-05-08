from django.db import models
from django.contrib.auth.models import AbstractUser

# ENTIDADE PERMISSÃO
class Permission(models.Model):
    codename = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.codename

    class Meta:
        ordering = ['codename']
        verbose_name = 'Permission'
        verbose_name_plural = 'Permissions'

# ENTIDADE ROLE
class Role(models.Model):
    id_role = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)
    permissions = models.ManyToManyField(
        Permission,
        blank=True,
        related_name='roles'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['id_role']
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'

# ENTIDADE USUÁRIO
class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15, blank=False, null=False, unique=True)
    birth_date = models.CharField(blank=False, null=False, max_length=10)
    document = models.CharField(max_length=50, blank=False, null=False, unique=True)
    role = models.ForeignKey(Role,
                             on_delete=models.CASCADE,
                             default=1, 
                             related_name='users')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username

    class Meta:
        ordering = ["id"]
        verbose_name = "User"
        verbose_name_plural = "Users"

# ENTIDADE ENDEREÇO
class Address(models.Model):
    id_address = models.AutoField(primary_key=True)
    street = models.CharField(max_length=100, blank=False, null=False)
    city = models.CharField(max_length=50, blank=False, null=False)
    state = models.CharField(max_length=50, blank=False, null=False)
    country = models.CharField(max_length=50, blank=False, null=False)
    neighborhood = models.CharField(max_length=50, blank=False, null=False)
    number = models.CharField(max_length=10, blank=True, null=True)
    postal_code = models.CharField(max_length=20, blank=False, null=False)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.street

    class Meta:
        ordering = ['id_address']
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses'