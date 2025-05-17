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
