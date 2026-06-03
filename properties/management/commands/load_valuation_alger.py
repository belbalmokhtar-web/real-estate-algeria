import re
from django.core.management.base import BaseCommand
from properties.models import (
    Wilaya, Commune, ZoneType, BuildingNature,
    BuildingCharacteristic, Valuation
)

class Command(BaseCommand):
    help = 'Load valuation data for Alger Centre from extracted PDF text'

    def handle(self, *args, **options):
        # 1. التأكد من وجود الولاية والبلدية
        wilaya, _ = Wilaya.objects.get_or_create(
            code="16",
            defaults={"name_ar": "الجزائر", "name_fr": "Alger"}
        )
        commune = Commune.objects.filter(wilaya=wilaya, code="556").first()
        if not commune:
            commune = Commune.objects.create(code="556", wilaya=wilaya, name_ar="الجزائر الوسطى",
                                             name_fr="Alger Centre")

        # 2. إنشاء أنواع المناطق (Zone)
        zones_data = [
            ("Zone résidentielle", "Zone résidentielle"),
            ("Centre ville", "Centre ville"),
            ("Zone périphérique", "Zone périphérique"),
            ("Zone d'éloignement", "Zone d'éloignement"),
        ]
        zones = {}
        for name_ar, name_fr in zones_data:
            zone, _ = ZoneType.objects.get_or_create(
                name_ar=name_ar, defaults={"name_fr": name_fr}
            )
            zones[name_ar] = zone

        # 3. إنشاء طبائع العقار (BuildingNature) وخصائصها (BuildingCharacteristic)
        # البيانات مستخرجة من النص (حسب ما هو واضح)
        # ملاحظة: بعض القيم غير مكتملة، سيتم إضافة ما هو موجود فقط

        # تعريف القيم: لكل طبيعة وخاصية، قائمة بالقيم حسب المناطق الأربع
        # الترتيب: Zone résidentielle (min,max), Centre ville (min,max), Zone périphérique (min,max), Zone d'éloignement (min,max)

        valuation_data = {
            "Individuels": {
                "Standing": [
                    (220000, 253000),  # Zone résidentielle
                    (205000, 235750),  # Centre ville
                    (190000, 218500),  # Zone périphérique
                    # (?, ?)  # Zone d'éloignement غير موجودة في النص
                ],
                "Amélioré": [
                    (205000, 235750),
                    (190000, 218550),
                    (175000, 201250),
                ],
                "Economique": [
                    (190000, 218500),
                    (175000, 201250),
                    (160000, 184000),
                ],
                "Précaire": [
                    (175000, 201250),
                    (160000, 184050),
                    (145000, 166750),
                ],
            },
            "Collectifs et Semi-Collectifs": {
                "Standing": [
                    (180000, 207000),
                    (165000, 189750),
                    (150000, 172500),
                ],
                "Amélioré": [
                    (165000, 189750),
                    (150000, 172550),
                    (135000, 155250),
                ],
                "Economique": [
                    (150000, 172500),
                    (135000, 155250),
                    (120000, 138000),
                ],
                "Précaire": [
                    (135000, 155250),
                    (120000, 138050),
                    (105000, 120750),
                ],
            },
            "Locaux Commerciaux et Locaux à Usage Professionnels": {
                "Artère hautement commerciale": [
                    (350000, 402500),
                    (450000, 517500),
                    (400000, 460000),
                ],
                "Artère moyennement commerciale": [
                    (300000, 345000),
                    (400000, 460050),
                    (350000, 402500),
                ],
                "Artère peu commerciale": [
                    (250000, 287500),
                    (350000, 402500),
                    (300000, 345000),
                ],
            },
            # Hangars: لا توجد قيم في النص (حقول فارغة)
            "Terrains Nus": {
                "Pleine propriété deux (02) façades avec raccordements": [
                    (220000, 253000),
                    (200000, 230000),
                    (180000, 207000),
                ],
                "Pleine propriété une (01) façade avec raccordements": [
                    (200000, 230000),
                    (180050, 207000),
                    (160000, 184050),
                ],
                "Pleine propriété deux (02) façades sans raccordements": [
                    (180000, 207000),
                    (160050, 184050),
                    (140000, 161000),
                ],
                "Pleine propriété une (01) façade sans raccordements": [
                    (160000, 184050),
                    (140050, 161000),
                    (120000, 138050),
                ],
                "Dans l'indivision": [
                    (140000, 161000),
                    (120050, 138050),
                    (100000, 115000),
                ],
                # "Industriel" لا توجد قيم
            },
            # Terrains Agricoles en Plaine و en Pente: لا توجد قيم في النص
        }

        # إنشاء طبائع العقار والخصائص والتقييمات
        for nature_name, characteristics in valuation_data.items():
            nature, _ = BuildingNature.objects.get_or_create(
                name_ar=nature_name,
                defaults={"name_fr": nature_name}
            )
            for char_name, values_list in characteristics.items():
                characteristic, _ = BuildingCharacteristic.objects.get_or_create(
                    nature=nature,
                    name_ar=char_name,
                    defaults={"name_fr": char_name}
                )
                # لكل منطقة من المناطق (حسب ترتيب القيم المتاحة)
                # نربط كل زوج من القيم بالمنطقة المقابلة
                zone_names = list(zones.keys())
                for idx, (min_val, max_val) in enumerate(values_list):
                    if idx >= len(zone_names):
                        break  # تجاوز إذا كان عدد المناطق أقل من القيم
                    zone = zones[zone_names[idx]]
                    valuation, created = Valuation.objects.get_or_create(
                        wilaya=wilaya,
                        commune=commune,
                        zone=zone,
                        nature=nature,
                        characteristic=characteristic,
                        defaults={
                            "min_price_per_sqm": min_val,
                            "max_price_per_sqm": max_val,
                        }
                    )
                    if not created:
                        # تحديث القيم إذا كانت موجودة مسبقاً
                        valuation.min_price_per_sqm = min_val
                        valuation.max_price_per_sqm = max_val
                        valuation.save()
                    self.stdout.write(f"{'Created' if created else 'Updated'}: {nature_name} - {char_name} - {zone.name_ar} => {min_val} - {max_val}")

        self.stdout.write(self.style.SUCCESS("Valuation data for Alger Centre loaded successfully."))