# SAAU — Sistema de Autenticação e Administração de Usuários

O **SAAU** é um módulo independente de autenticação e gestão de usuários, com foco em segurança, conformidade com a LGPD e boas práticas de desenvolvimento. Projetado em **Django**, ele oferece funcionalidades essenciais para sistemas que necessitam de controle de acesso robusto, seguro e escalável.

Este projeto foi desenvolvido como parte de uma atividade acadêmica da **Universidade de Mogi das Cruzes**.

## Funcionalidades

- Cadastro de usuários com validação de CPF e senha forte  
- Autenticação via e-mail e senha com geração de **JWT**  
- Controle de acesso baseado em papéis (**RBAC**)  
- Redefinição de senha via e-mail com token temporário  
- Exclusão de conta conforme LGPD  
- Pseudoanonimização de dados sensíveis  
- Registro de logs de acesso e alterações  
- API RESTful com suporte a JSON  

## Tecnologias Utilizadas

- Django 5.2
- python-decouple 3.8
- djangorestframework 3.16.0
- djangorestframework-simplejwt 5.5.0
- PyJWT 2.9.0
- django-ratelimit 4.1.0

## Instalação

Instale as dependências com:

```bash
pip install -r requirements.txt
```

## requirements.txt

```ini
Django==5.2
python-decouple==3.8
djangorestframework==3.16.0
djangorestframework-simplejwt==5.5.0
PyJWT==2.9.0
django-ratelimit==4.1.0
```

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

## Autenticação

```makefile
Authorization: Bearer <token>
```

## Estrutura de Dados
O sistema utiliza um modelo relacional baseado nas entidades:

- **User**: Dados pessoais como nome, e-mail, CPF, senha (hash), data de nascimento, etc.

- **Role**: Define o papel do usuário no sistema, como *master* ou *cliente*.

- **Address**: Armazena endereço do usuário, opcional no cadastro.

As senhas são armazenadas com algoritmos de **hash** + **salt**, e dados sensíveis são anonimizados ou pseudoanonimizados para garantir conformidade com a LGPD.

## Conformidade com LGPD

- Exclusão de conta com remoção e/ou anonimização de dados

- Restrição de acesso a informações pessoais

- Armazenamento seguro de senhas

- Pseudoanonimização de dados como CPF e endereço para uso não identificável

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

## Observações Finais
- O sistema é totalmente aderente à LGPD.
- Apenas usuários com papel "master" podem criar papéis e acessar rotas administrativas.
- Todas as operações sensíveis são registradas em log.

Para detalhes técnicos e exemplos de código, consulte o arquivo [`Documents/how_does_it_work.md`](https://github.com/FlamingoLindo/SAAU/blob/main/Documents/how_does_it_work.md).

Para saber como rodar a aplicação, consulte o arquivo [`Documents/how_to_run.md`](https://github.com/FlamingoLindo/SAAU/blob/main/Documents/how_to_run.md).

## Integrantes do Projeto

- [Vitor Antunes Ferreira](https://github.com/FlamingoLindo) RGM: 11221100950

- [Lucas Lizot Mori](https://github.com/LLizot) RGM: 11212100125

- [Carlos Henrique](https://github.com/carloosz) RGM: 11221504686

- [Bryan Henrique de Oliveira Serrão](https://github.com/bryanhenriquek) RGM: 11221101589

