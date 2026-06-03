# accounts/signals.py
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from .models import User, AgentProfile, DeveloperProfile
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


@receiver(post_save, sender=User)
def create_user_profiles(sender, instance, created, **kwargs):
    """
    إنشاء الملفات الشخصية للمستخدم عند التسجيل
    """
    if created:
        # إنشاء ملف الوكيل
        if instance.role == 'agent':
            try:
                agent_profile, created_agent = AgentProfile.objects.get_or_create(user=instance)
                if created_agent:
                    logger.info(f"✅ تم إنشاء ملف وكيل للمستخدم: {instance.username}")
            except Exception as e:
                logger.error(f"❌ خطأ في إنشاء ملف الوكيل للمستخدم {instance.username}: {e}")

        # إنشاء ملف المطور
        elif instance.role == 'developer':
            try:
                developer_profile, created_dev = DeveloperProfile.objects.get_or_create(user=instance)
                if created_dev:
                    logger.info(f"✅ تم إنشاء ملف مطور للمستخدم: {instance.username}")
            except Exception as e:
                logger.error(f"❌ خطأ في إنشاء ملف المطور للمستخدم {instance.username}: {e}")


@receiver(post_save, sender=User)
def update_user_profiles(sender, instance, **kwargs):
    """
    تحديث الملفات الشخصية عند تحديث بيانات المستخدم
    """
    # تحديث ملف الوكيل
    if instance.role == 'agent':
        try:
            if hasattr(instance, 'agent_profile'):
                instance.agent_profile.save()
            else:
                AgentProfile.objects.create(user=instance)
                logger.info(f"✅ تم إنشاء ملف وكيل للمستخدم (بعد التحديث): {instance.username}")
        except Exception as e:
            logger.error(f"❌ خطأ في تحديث ملف الوكيل للمستخدم {instance.username}: {e}")

    # تحديث ملف المطور
    elif instance.role == 'developer':
        try:
            if hasattr(instance, 'developer_profile'):
                instance.developer_profile.save()
            else:
                DeveloperProfile.objects.create(user=instance)
                logger.info(f"✅ تم إنشاء ملف مطور للمستخدم (بعد التحديث): {instance.username}")
        except Exception as e:
            logger.error(f"❌ خطأ في تحديث ملف المطور للمستخدم {instance.username}: {e}")


@receiver(pre_save, sender=User)
def check_role_change(sender, instance, **kwargs):
    """
    التحقق من تغيير دور المستخدم قبل الحفظ
    """
    if instance.pk:
        try:
            old_instance = User.objects.get(pk=instance.pk)
            if old_instance.role != instance.role:
                logger.info(f"🔄 تم تغيير دور المستخدم {instance.username} من {old_instance.role} إلى {instance.role}")
                instance._old_role = old_instance.role
        except User.DoesNotExist:
            pass


@receiver(post_save, sender=AgentProfile)
def update_agent_stats(sender, instance, created, **kwargs):
    """
    تحديث إحصائيات الوكيل عند إنشاء أو تحديث ملفه
    """
    if created:
        logger.info(f"✅ تم إنشاء ملف وكيل جديد: {instance.user.username}")
    else:
        # تحديث عدد العقارات للوكيل
        from properties.models import Property
        property_count = Property.objects.filter(agent=instance, is_active=True).count()
        if instance.properties_count != property_count:
            instance.properties_count = property_count
            instance.save(update_fields=['properties_count'])
            logger.info(f"🔄 تم تحديث عدد عقارات الوكيل {instance.user.username}: {property_count}")


@receiver(post_save, sender=DeveloperProfile)
def update_developer_stats(sender, instance, created, **kwargs):
    """
    تحديث إحصائيات المطور عند إنشاء أو تحديث ملفه
    """
    if created:
        logger.info(f"✅ تم إنشاء ملف مطور جديد: {instance.user.username}")
    else:
        from properties.models import Property
        property_count = Property.objects.filter(owner=instance.user, is_active=True).count()
        if instance.properties_count != property_count:
            instance.properties_count = property_count
            instance.save(update_fields=['properties_count'])
            logger.info(f"🔄 تم تحديث عدد عقارات المطور {instance.user.username}: {property_count}")


@receiver(post_delete, sender=User)
def cleanup_user_profiles(sender, instance, **kwargs):
    """
    تنظيف الملفات الشخصية عند حذف المستخدم
    """
    logger.info(f"🗑️ يتم حذف الملفات الشخصية للمستخدم: {instance.username}")

    if hasattr(instance, 'agent_profile'):
        instance.agent_profile.delete()
        logger.info(f"🗑️ تم حذف ملف الوكيل للمستخدم: {instance.username}")

    if hasattr(instance, 'developer_profile'):
        instance.developer_profile.delete()
        logger.info(f"🗑️ تم حذف ملف المطور للمستخدم: {instance.username}")


def create_admin_user():
    """إنشاء مستخدم مشرف افتراضي إذا لم يكن موجوداً"""
    from django.contrib.auth import get_user_model
    User = get_user_model()

    if not User.objects.filter(is_superuser=True).exists():
        try:
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123',
                first_name='مدير',
                last_name='النظام',
                role='user'
            )
            print("✅ تم إنشاء المستخدم المشرف الافتراضي: admin / admin123")
        except Exception as e:
            print(f"⚠️ خطأ في إنشاء المستخدم المشرف الافتراضي: {e}")