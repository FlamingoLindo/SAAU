from rest_framework import serializers
from .models import Role, CustomUser, Address

from sensitive_info.models import CPFToken, EmailToken, PhoneToken, BirthDateToken


class RoleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Role
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)
    document = serializers.CharField(write_only=True)
    phone = serializers.CharField(write_only=True)
    birth_date = serializers.DateField(write_only=True)

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
        extra_kwargs = {'password': {'write_only': True}, 
                        'birth_date': {'write_only': True}, 
                        'document': {'write_only': True}, 
                        'phone': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser(**validated_data)
        user.set_password(password)
        user.save()
        return user

class AddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = Address
        fields = '__all__'