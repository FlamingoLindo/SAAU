from django.db import models

# Create your models here.
class CPFToken(models.Model):
    token = models.UUIDField(primary_key=True, editable=False)
    cpf_real = models.CharField(max_length=11)  # sem formatação
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.token)