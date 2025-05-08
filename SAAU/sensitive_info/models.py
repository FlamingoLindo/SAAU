from django.db import models

class CPFToken(models.Model):
    token = models.UUIDField(primary_key=True, editable=False)
    cpf_real = models.CharField(max_length=11, unique=True)  # sem formatação
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.token)

class EmailToken(models.Model):
    token = models.UUIDField(primary_key=True, editable=False)
    email_real = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.token)
    
class PhoneToken(models.Model):
    token       = models.UUIDField(primary_key=True, editable=False)
    phone_real  = models.CharField(max_length=15, unique=True)   # sem formatação
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.token)

class BirthDateToken(models.Model):
    token         = models.UUIDField(primary_key=True, editable=False)
    birth_date_real = models.DateField()
    created_at    = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.token)