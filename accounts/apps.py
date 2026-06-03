# accounts/apps.py
from django.apps import AppConfig
from django.db.models.signals import post_migrate


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        """
        تحميل الإشارات عند بدء التطبيق
        """
        import accounts.signals

        # تسجيل إشارة بعد الترحيلات لإنشاء المستخدم المشرف
        post_migrate.connect(create_admin_user, sender=self)


def create_admin_user(sender, **kwargs):
    """
    إنشاء مستخدم مشرف افتراضي بعد الترحيلات
    """
    from accounts.signals import create_admin_user as create_admin
    create_admin()