# Como utilizar o SAAU

1. Configuração e migrações

    1. Acesse o diretório do projeto:
    ```bash
    cd SAAU
    ```

    2. Crie as migrações a partir dos seus models Django (Apenas se os bancos de dado não estiverem criados):
    ```bash
    py manage.py makemigrations
    ```

    3. Aplique as migrações no banco de dados padrão (Apenas se os bancos de dado não estiverem criados):
    ```bash 
    py manage.py migrate
    ```

    4. Aplique as migrações também no banco de dados sensitive (Apenas se os bancos de dado não estiverem criados):
    ```bash 
    py manage.py migrate --database sensitive
    ```

2. Executando o servidor de desenvolvimento:

Para iniciar o servidor local e testar a API:
```bash
py manage.py runserver
```
Por padrão o Django irá rodar em http://127.0.0.1:8000/.

3. Rotas da API

A seguir, exemplos de como usar as principais rotas para gerenciamento de usuários. Use sua ferramenta HTTP favorita (cURL, Postman, HTTPie, etc.).

- **Criar usuário**

    - **Método**: `POST`
    - **Endpoint**: `/api/users/create/`
    - **Body (JSON)**:
    ```json
    {
        "username": "Flamingo",
        "email": "flamingo@gmail.com",
        "password": "12345678",
        "phone": "8127273982",
        "document": "73359032209",
        "birth_date": "2000-02-15",
        "role": "master"
    }
    ```
    
    - **Resposta de sucesso (201 Created)**:
    ```json
    {
        "user": {
            "id": 2,
            "email": "06e706e9-4139-4402-b1e8-d50c800a2048",
            "username": "Flamingo",
            "birth_date": "a63bde7e-22b2-4c1b-ba63-ee2237817d4e",
            "role": "master",
            "document": "fa4ca764-52cd-4ad3-92aa-452c8b960135",
            "phone": "0e929fa1-0677-40ba-9cf7-83d52adb9a45",
            "is_staff": true,
            "is_active": true
        }
    }
    ```

- **Login**

    - **Método**: `POST`
    - **Endpoint**: `/api/login/`
    - **Body (JSON)**:
    ```json
    {
        "email": "flamingo@gmail.com",
        "password": "12345678"
    }
    ```
    
    - **Resposta de sucesso (200 OK)**:
    ```json
    {
        "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc0NjkyNTgyMCwiaWF0IjoxNzQ2ODM5NDIwLCJqdGkiOiI3MDYxM2Y3N2NhMGQ0MjllYjZiZDM0ZDU4Yjg5ZDNiNyIsInVzZXJfaWQiOjJ9.JZenqpUi6GLQNq2XyzmYzSpCKzT5BigW-X5LdCUBINE",
        "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQ2ODM5NzIwLCJpYXQiOjE3NDY4Mzk0MjAsImp0aSI6IjQ4N2EzMmYxOGMxNDRhYjdiN2E3NjY4M2JmMzAyY2E4IiwidXNlcl9pZCI6Mn0.q2NlQpcNMZb3zSBpVYWyDdcIw6ILq3ki9KLzl5RZxj4",
        "user": {
            "id": 2,
            "email": "06e706e9-4139-4402-b1e8-d50c800a2048",
            "username": "Flamingo",
            "birth_date": "a63bde7e-22b2-4c1b-ba63-ee2237817d4e",
            "role": "master",
            "document": "fa4ca764-52cd-4ad3-92aa-452c8b960135",
            "phone": "0e929fa1-0677-40ba-9cf7-83d52adb9a45",
            "is_staff": true,
            "is_active": true
        }
    }
    ```

- **Alterar senha**

    - **Método**: `PUT`
    - **Endpoint**: `/api/reset_password/`
    - **Headers**:
    ```sql
    Authorization: Bearer <seu_token_JWT>
    Content-Type: application/json
    ```
    - **Body (JSON)**:
    ```json
    {
        "old_password": "12345678",
        "new_password": "123456789",
        "confirm_password": "123456789"
    }
    ```
    
    - **Resposta de sucesso (200 OK)**:
    ```json
    {
        "message": "Senha alterada com sucesso."
    }
    ```

- **Excluir conta**

    - **Método**: `DELETE`
    - **Endpoint**: `/api/users/delete_account/`
    - **Headers**:
    ```sql
    Authorization: Bearer <seu_token_JWT>
    Content-Type: application/json
    ```
    - **Resposta de sucesso (204 No Content)**:
    ```json
    
    ```

## 4. Documentação interativa da API

- **Swagger UI**  
  - **Método**: `GET`  
  - **Endpoint**: `http://127.0.0.1:8000/swagger/`  
  - Navegue nessa URL para ver toda a sua API documentada com Swagger, testar os endpoints e visualizar esquemas de request/response.

- **OpenAPI JSON**  
  - **Método**: `GET`  
  - **Endpoint**: `http://127.0.0.1:8000/swagger/?format=openapi`  
  - Retorna o schema OpenAPI em formato JSON, útil para geração de clientes ou integração com outras ferramentas.

- **ReDoc UI**  
  - **Método**: `GET`  
  - **Endpoint**: `http://127.0.0.1:8000/redoc/`  
  - Uma alternativa ao Swagger UI, com navegação lateral para especificações mais longas.

## 5. Teste online do SAAU

O projeto está rodando em um droplet da Digital Ocean e pode ser testado publicamente:

- **API online:** http://64.227.8.209:8000/
- **Documentação interativa (ReDoc):** http://64.227.8.209:8000/redoc/

Você pode testar todos os endpoints diretamente pelo link acima, utilizando ferramentas como Postman, Insomnia.

## Endpoints da API

| Método | Rota                                   | Descrição                                                      | Autenticação |
| ------ | -------------------------------------- | -------------------------------------------------------------- | ------------ |
| POST   | `/api/token/`                         | Obtenção de token JWT (login via SimpleJWT)                    | ❌           |
| POST   | `/api/token/refresh/`                 | Refresh do token JWT                                           | ❌           |
| POST   | `/api/login/`                         | Login customizado de usuário                                   | ❌           |
| POST   | `/api/users/create/`                  | Criação de um usuário                                          | ❌           |
| POST   | `/api/role/create/`                   | Criação de um papel                                            | ✅           |
| PUT    | `/api/reset_password/`                | Redefinição de senha do usuário logado                         | ✅           |
| GET    | `/api/users/listUser/`                | Listagem de usuários (apenas staff/master, dados mascarados)   | ✅           |
| DELETE | `/api/users/deleteUser/<id>/`         | Exclusão de um usuário específico (master ou o próprio)        | ✅           |
| DELETE | `/api/users/delete_account/`          | Exclusão da própria conta do usuário logado                    | ✅           |
| GET    | `/api/users/<id>/`                    | Detalhes de um usuário específico                              | ✅           |
| POST   | `/api/users/<pk>/toggle-active/`      | Ativa/desativa usuário (altera status ativo)                   | ✅           |

## Teste Online

O SAAU está disponível para testes públicos em um droplet da Digital Ocean:
- **API online:** http://64.227.8.209:8000/
- **Documentação interativa (ReDoc):** http://64.227.8.209:8000/redoc/

Você pode testar todos os endpoints diretamente pelo link acima, utilizando ferramentas como Postman, Insomnia ou a interface web ReDoc.

## Segurança, Pseudoanonimização e LGPD

- Dados sensíveis (CPF, e-mail, telefone, data de nascimento) são armazenados em um banco separado (`sensitive.sqlite3`) usando models específicos do app `sensitive_info`.
- Esses dados são referenciados por tokens UUID na tabela principal de usuários, garantindo que informações sensíveis nunca fiquem expostas diretamente.
- Relações cruzadas entre bancos são bloqueadas por um router customizado.
- Todas as operações sensíveis são registradas em log.
- O sistema é totalmente aderente à LGPD.

## Configuração de Bancos de Dados e JWT

No arquivo `settings.py`, o projeto utiliza múltiplos bancos de dados e autenticação JWT:
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
    "ALGORITHM": "HS256",
    "AUTH_HEADER_TYPES": ("Bearer",),
    # ...
}
```

## Models de Dados Sensíveis

Os modelos do app `sensitive_info` armazenam dados sensíveis de forma pseudoanonimizada:
```python
class CPFToken(models.Model):
    token = models.UUIDField(primary_key=True, editable=False)
    cpf_real = models.CharField(max_length=11, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
# ... EmailToken, PhoneToken, BirthDateToken ...
```

## Fluxo de Cadastro e Exclusão

- No cadastro, dados sensíveis são salvos no banco `sensitive` e substituídos por tokens no usuário.
- Ao listar usuários, dados sensíveis são mascarados.
- Ao excluir a conta, todos os dados sensíveis são removidos do banco `sensitive`.
