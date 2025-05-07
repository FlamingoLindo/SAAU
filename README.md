# SAAU — Sistema de Autenticação e Administração de Usuários

O **SAAU** é um módulo independente de autenticação e gestão de usuários, com foco em segurança, conformidade com a LGPD e boas práticas de desenvolvimento. Projetado em **Django**, ele oferece funcionalidades essenciais para sistemas que necessitam de controle de acesso robusto, seguro e escalável.

Este projeto foi desenvolvido como parte de uma atividade acadêmica da **Universidade de Mogi das Cruzes**,.

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

- Python 3.12+
- Django 5.2
- Django REST Framework 3.16.0
- djangorestframework-simplejwt 5.5.0
- python-decouple 3.8
- PyJWT 2.9.0

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

| Método | Rota                          | Descrição                              | Autenticação |
| ------ | ----------------------------- | -------------------------------------- | ------------ |
| POST   | `/api/users/create/`              | Usada para a criação de um usuário         | ❌|
| POST    | `/api/role/create/`              | Usada para a criação de um papel         | ✅|
| POST    | `/api/login/`              | Usada para realizar o login de um usuário no sistema         | ❌|
| ... | `/api/`              | ...         | ✅|

## Autenticação

```makefile
Authorization: Bearer <token>
```

## Estrutura de Dados
O sistema utiliza um modelo relacional baseado nas entidades:

- **User**: dados pessoais como nome, e-mail, CPF, senha (hash), data de nascimento, etc.

- **Role**: define o papel do usuário no sistema, como *master* ou *cliente*.

- **Address**: armazena endereço do usuário, opcional no cadastro.

As senhas são armazenadas com algoritmos de **hash** + **salt**, e dados sensíveis são anonimizados ou pseudoanonimizados para garantir conformidade com a LGPD.

## Conformidade com LGPD

- Exclusão de conta com remoção e/ou anonimização de dados

- Restrição de acesso a informações pessoais

- Armazenamento seguro de senhas

- Pseudoanonimização de dados como CPF e endereço para uso não identificável

## Integrantes do Projeto

- Vitor Antunes Ferreira

- Lucas Lizot Mori

- Carlos Henrique

- Bryan Henrique de Oliveira Serrão