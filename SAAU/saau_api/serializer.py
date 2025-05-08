from rest_framework import serializers
from .models import Role, CustomUser, Address

from sensitive_info.models import CPFToken, EmailToken, PhoneToken, BirthDateToken


class RoleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Role
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):

    def validate(self, attrs):
        if (
            EmailToken.objects.using('sensitive') \
                .filter(email_real=attrs['email']).exists() or
            CPFToken.objects.using('sensitive') \
                .filter(cpf_real=attrs['document']).exists() or
            PhoneToken.objects.using('sensitive') \
                .filter(phone_real=attrs['phone']).exists()
        ):
            raise serializers.ValidationError("Dados inválidos!")
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user

    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'username', 'password', 'birth_date', 'document', 'phone', 'is_staff', 'is_active']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user
    
class UserReadSerializer(serializers.ModelSerializer):
    email      = serializers.SerializerMethodField()
    document   = serializers.SerializerMethodField()
    phone      = serializers.SerializerMethodField()
    birth_date = serializers.SerializerMethodField()

    class Meta:
        model  = CustomUser
        fields = [
            'id', 'username',
            'email', 'birth_date',
            'document', 'phone',
            'is_staff', 'is_active',
        ]

    def get_email(self, obj):
        # recupera e-mail real
        real = EmailToken.objects.using('sensitive') \
            .get(token=obj.email).email_real
        local, domain = real.split('@', 1)
        # máscara: só primeira letra visível
        return f"{local[0]}{'*'*(len(local)-1)}@{domain}"

    def get_document(self, obj):
        real = CPFToken.objects.using('sensitive') \
            .get(token=obj.document).cpf_real
        # CPF tem 11 dígitos, mostre 3 iniciais e 2 finais
        return f"{real[:3]}{'*'*6}{real[-2:]}"

    def get_phone(self, obj):
        real = PhoneToken.objects.using('sensitive') \
            .get(token=obj.phone).phone_real
        # máscara: 3 primeiros e 4 últimos
        return f"{real[:3]}{'*'*(len(real)-7)}{real[-4:]}"

    def get_birth_date(self, obj):
        real = BirthDateToken.objects.using('sensitive') \
            .get(token=obj.birth_date).birth_date_real
        # transforma date em string dd/mm/YYYY e mascara o dia
        s = real.strftime("%d/%m/%Y")
        return f"**/{s[3:]}"

class AddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = Address
        fields = '__all__'