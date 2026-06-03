#!/usr/bin/env python
"""Django's command-line utility for administrative tasks with enhanced features."""

import os
import sys
from pathlib import Path


# ============================================================================
# 1. محاولة تحميل متغيرات البيئة من ملف .env (إذا كان موجوداً)
# ============================================================================
def load_env_file():
    """Load environment variables from a .env file if present."""
    env_path = Path(__file__).parent / '.env'
    if env_path.exists():
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ.setdefault(key.strip(), value.strip())
        except Exception as e:
            sys.stderr.write(f"Warning: Could not load .env file: {e}\n")


# ============================================================================
# 2. التحقق من البيئة الافتراضية وإصدار Python
# ============================================================================
def check_environment():
    """Perform basic environment checks and display warnings if needed."""
    # التحقق من وجود البيئة الافتراضية
    in_venv = hasattr(sys, 'real_prefix') or (
            hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )
    if not in_venv:
        sys.stderr.write(
            "Warning: It looks like you are not using a virtual environment.\n"
            "It's recommended to create and activate one before continuing.\n"
        )

    # التحقق من إصدار Python
    if sys.version_info < (3, 8):
        sys.stderr.write(
            f"Warning: Python {sys.version_info.major}.{sys.version_info.minor} is deprecated.\n"
            "Django 4.2+ requires Python 3.8 or higher.\n"
        )
    elif sys.version_info < (3, 10):
        sys.stderr.write(
            f"Note: You are using Python {sys.version_info.major}.{sys.version_info.minor}. "
            "Python 3.10+ is recommended for better performance.\n"
        )


# ============================================================================
# 3. الدالة الرئيسية المحسنة
# ============================================================================
def main():
    """Run administrative tasks with enhanced error handling and environment checks."""
    # تحميل متغيرات البيئة أولاً (قبل إعداد Django)
    load_env_file()

    # تعيين متغير الإعدادات الافتراضي إذا لم يكن موجوداً
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

    # التحقق من البيئة (اختياري، يمكن تعطيله في الإنتاج)
    if os.environ.get('DJANGO_ENV') != 'production':
        check_environment()

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        # تحسين رسالة الخطأ مع توجيهات مفيدة
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?\n\n"
            "You can install Django with: pip install django\n"
            "Or install all dependencies with: pip install -r requirements.txt"
        ) from exc

    # تمرير وسائط سطر الأوامر إلى Django
    execute_from_command_line(sys.argv)


# ============================================================================
# 4. دعم الأوامر المخصصة عبر نقطة الدخول
# ============================================================================
if __name__ == '__main__':
    main()