import re

with open('properties/management/commands/insert_communes.py', 'r', encoding='utf-8') as f:
    content = f.read()

# استبدال علامات التنصيص المنحنية بالمستقيمة
content = content.replace('“', '"').replace('”', '"')

with open('properties/management/commands/insert_communes_fixed.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("تم التصحيح. استخدم الملف insert_communes_fixed.py")