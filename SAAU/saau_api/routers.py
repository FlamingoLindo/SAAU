"""
Database Router para separar dados sensíveis do app `sensitive_info`:

- Modelos do app `sensitive_info` --> banco de dados “sensitive”
- Todos os outros modelos --> banco de dados “default”
- Impede relações cruzadas entre esses dois bancos
- Controla em qual conexão cada migração deve ser aplicada
"""

class SensitiveDataRouter:
    sensitive_apps = {'sensitive_info'}

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.sensitive_apps:
            return 'sensitive'
        return 'default'

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.sensitive_apps:
            return 'sensitive'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        # relações entre modelos de bancos diferentes são bloqueadas
        db_obj1 = obj1._state.db
        db_obj2 = obj2._state.db
        if db_obj1 and db_obj2 and db_obj1 != db_obj2:
            return False
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in self.sensitive_apps:
            return db == 'sensitive'
        # todos os outros apps devem migrar somente no default
        return db == 'default'
