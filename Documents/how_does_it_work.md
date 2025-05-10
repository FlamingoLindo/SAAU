# Como o SAAU funciona

## Visão Geral
O **SAAU** (Sistema de Autenticação e Administração de Usuários) é um módulo independente desenvolvido em Django para autenticação, controle de acesso e gestão de usuários, com foco em segurança, privacidade e conformidade com a LGPD. Ele oferece uma API RESTful robusta, baseada em papéis (RBAC), com pseudoanonimização de dados sensíveis e registro de logs.

## Principais Funcionalidades
- Cadastro de usuários com validação de CPF e senha forte
- Autenticação via e-mail e senha (JWT)
- Controle de acesso por papéis (Role-Based Access Control)
- Redefinição de senha via e-mail
- Exclusão de conta conforme LGPD
- Pseudoanonimização de dados sensíveis (CPF, e-mail, telefone, data de nascimento)
- Listagem de usuários (com dados mascarados)
- Registro de logs de acesso e alterações

## Estrutura de Dados
O sistema utiliza um modelo relacional com as seguintes entidades principais:
- **User**: dados pessoais (nome, e-mail, CPF, senha, data de nascimento, telefone, papel)
- **Role**: define o papel do usuário (ex: master, cliente) e suas permissões
- **Address**: endereço do usuário (opcional)
- **Tokens Sensíveis**: tabelas separadas para armazenar dados reais de CPF, e-mail, telefone e data de nascimento, referenciados por tokens UUID

## Configurações no settings.py
O projeto utiliza dois bancos de dados distintos para garantir a separação dos dados sensíveis:
- O banco `default` armazena os dados comuns do sistema.
- O banco `sensitive` armazena apenas os dados sensíveis (CPF, e-mail, telefone, data de nascimento), definidos no app `sensitive_info`.

Exemplo de configuração no `settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    },
    'sensitive': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'sensitive.sqlite3',
    }
}

DATABASE_ROUTERS = ['saau_api.routers.SensitiveDataRouter']
```

O arquivo `routers.py` define a lógica para garantir que os modelos do app `sensitive_info` sejam sempre gravados/lidos do banco `sensitive`, impedindo relações cruzadas entre bancos.

Além disso, o projeto define o modelo de usuário customizado:
```python
AUTH_USER_MODEL = 'saau_api.CustomUser'
```

### Configuração do JWT
A autenticação do sistema é feita via JWT, utilizando o pacote `djangorestframework-simplejwt`. No `settings.py`, a configuração inclui:

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=5),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "ALGORITHM": "HS256",
    "AUTH_HEADER_TYPES": ("Bearer",),
    # ...outras opções...
}
```
Essas opções controlam o tempo de expiração dos tokens, o algoritmo de assinatura, o tipo de header e o comportamento de rotação/blacklist dos tokens.

## Models em sensitive_info/models.py
O app `sensitive_info` contém os modelos responsáveis por armazenar os dados sensíveis de forma pseudoanonimizada, cada um com seu próprio token UUID:

```python
class CPFToken(models.Model):
    token = models.UUIDField(primary_key=True, editable=False)
    cpf_real = models.CharField(max_length=11, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

class EmailToken(models.Model):
    token = models.UUIDField(primary_key=True, editable=False)
    email_real = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

class PhoneToken(models.Model):
    token = models.UUIDField(primary_key=True, editable=False)
    phone_real = models.CharField(max_length=15, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

class BirthDateToken(models.Model):
    token = models.UUIDField(primary_key=True, editable=False)
    birth_date_real = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
```

Esses modelos garantem que os dados sensíveis nunca fiquem armazenados diretamente na tabela principal de usuários, reforçando a segurança e a conformidade com a LGPD.

## Fluxo de Cadastro e Pseudoanonimização
1. O usuário envia seus dados para cadastro.
2. Dados sensíveis (CPF, e-mail, telefone, data de nascimento) são armazenados em um banco separado (`sensitive.sqlite3`) e substituídos por tokens UUID na tabela principal de usuários.
3. A senha é armazenada de forma segura (hash + salt).
4. O usuário recebe confirmação do cadastro.

## Autenticação e Controle de Acesso
- O login é feito via e-mail e senha. O sistema busca o token do e-mail real, localiza o usuário e valida a senha.
- Após login, são gerados tokens JWT (access e refresh) para autenticação nas próximas requisições.
- O controle de acesso é feito por papéis (roles) e permissões, podendo restringir rotas a usuários staff/master.

## Rotas Principais da API
- **POST /api/users/create/** — Criação de usuário
- **POST /api/login/** — Login e obtenção de tokens JWT
- **PUT /api/reset_password/** — Redefinição de senha (autenticado)
- **DELETE /api/users/delete_account/** — Exclusão da própria conta (autenticado)
- **GET /api/users/** — Listagem de usuários (apenas staff/master, dados mascarados)

## Máscara e Pseudoanonimização
- Dados sensíveis nunca são expostos diretamente pela API.
- Ao listar usuários, e-mail, CPF, telefone e data de nascimento são exibidos de forma mascarada.
- A exclusão de conta remove o usuário e apaga os dados sensíveis do banco separado.

## Conformidade com LGPD
- Exclusão/anomização de dados sensíveis
- Restrição de acesso a informações pessoais
- Armazenamento seguro de senhas
- Pseudoanonimização para uso não identificável

## Exemplos de Código

### Cadastro de Usuário com Pseudoanonimização
Este trecho mostra como, ao cadastrar um usuário, os dados sensíveis (CPF, e-mail, telefone) são armazenados em um banco separado e substituídos por tokens na tabela principal:
```python
# views/auth.py
@api_view(['POST'])
@permission_classes([AllowAny])
def create_user(request):
    serializer = UserSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    data = serializer.validated_data.copy()
    # Pseudonimização do CPF: salva o CPF real no banco sensível e armazena o token no usuário
    cpf_real  = data.pop('document')
    cpf_token = uuid.uuid4()
    CPFToken.objects.using('sensitive').create(token=cpf_token, cpf_real=cpf_real)
    data['document'] = str(cpf_token)
    # Pseudonimização do E-mail: salva o e-mail real no banco sensível e armazena o token no usuário
    email_real  = data.pop('email')
    email_token = uuid.uuid4()
    EmailToken.objects.using('sensitive').create(token=email_token, email_real=email_real)
    data['email'] = str(email_token)
    # Pseudonimização do Telefone: salva o telefone real no banco sensível e armazena o token no usuário
    phone_real  = data.pop('phone')
    phone_token = uuid.uuid4()
    PhoneToken.objects.using('sensitive').create(token=phone_token, phone_real=phone_real)
    data['phone'] = str(phone_token)
    # ...continua...
```

### Máscara de Dados Sensíveis ao Listar Usuários
Este exemplo mostra como os dados sensíveis são mascarados ao serem exibidos pela API, protegendo a privacidade do usuário:
```python
# serializer.py
class UserReadSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()
    document = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    birth_date = serializers.SerializerMethodField()
    # Retorna o e-mail mascarado (apenas a primeira letra e domínio visíveis)
    def get_email(self, obj):
        real = EmailToken.objects.using('sensitive').get(token=obj.email).email_real
        local, domain = real.split('@', 1)
        return f"{local[0]}{'*'*(len(local)-1)}@{domain}"
    # Retorna o CPF mascarado (apenas 3 primeiros e 2 últimos dígitos visíveis)
    def get_document(self, obj):
        real = CPFToken.objects.using('sensitive').get(token=obj.document).cpf_real
        return f"{real[:3]}{'*'*6}{real[-2:]}"
    # Retorna o telefone mascarado (3 primeiros e 4 últimos dígitos visíveis)
    def get_phone(self, obj):
        real = PhoneToken.objects.using('sensitive').get(token=obj.phone).phone_real
        return f"{real[:3]}{'*'*(len(real)-7)}{real[-4:]}"
    # Retorna a data de nascimento mascarada (apenas mês e ano visíveis)
    def get_birth_date(self, obj):
        real = BirthDateToken.objects.using('sensitive').get(token=obj.birth_date).birth_date_real
        s = real.strftime("%d/%m/%Y")
        return f"**/{s[3:]}"
```

### Exclusão de Conta e Remoção de Dados Sensíveis
Este trecho mostra como, ao excluir a conta, todos os dados sensíveis do usuário são removidos do banco separado, garantindo conformidade com a LGPD:
```python
# views/users.py
def delete_account(request):
    user = request.user
    # Remove os dados sensíveis do banco 'sensitive' (CPF, e-mail, telefone, data de nascimento)
    CPFToken.objects.using('sensitive').filter(token=user.document).delete()
    EmailToken.objects.using('sensitive').filter(token=user.email).delete()
    PhoneToken.objects.using('sensitive').filter(token=user.phone).delete()
    BirthDateToken.objects.using('sensitive').filter(token=user.birth_date).delete()
    # Remove o usuário do banco principal
    user.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
```

### Redefinição de Senha
Este exemplo mostra como é feita a validação e alteração de senha de forma segura, exigindo a senha antiga e confirmação da nova:
```python
# views/auth.py
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def reset_password(request):
    user = request.user
    old_pw = request.data.get('old_password')
    new_pw = request.data.get('new_password')
    confirm_pw = request.data.get('confirm_password')
    # Verifica se a senha antiga está correta
    if not user.check_password(old_pw):
        return Response({"error": "Credenciais incorretas."}, status=status.HTTP_401_UNAUTHORIZED)
    # Verifica se a nova senha e a confirmação coincidem
    if new_pw != confirm_pw:
        return Response({"error": "As senhas não coincidem."}, status=status.HTTP_400_BAD_REQUEST)
    # Atualiza a senha do usuário
    user.set_password(new_pw)
    user.save(update_fields=['password'])
    return Response({"message": "Senha alterada com sucesso."}, status=status.HTTP_200_OK)
```

## Observações
- Apenas usuários com papel "master" podem criar papéis e acessar rotas administrativas.
- O sistema registra logs de todas as operações sensíveis.
- Dados sensíveis são sempre tratados de acordo com a LGPD.

---

Para detalhes de endpoints e exemplos de uso, consulte o arquivo `how_to_run.md`.
