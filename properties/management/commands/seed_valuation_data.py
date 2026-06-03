# properties/management/commands/seed_valuation_data.py
import random
from django.core.management.base import BaseCommand
from properties.models_valuation import Wilaya, Commune, Zone, NatureImmeuble, Caracteristique, ValuationRange


class Command(BaseCommand):
    help = 'إضافة بيانات تجريبية لنطاقات التقييم'

    def handle(self, *args, **options):
        self.stdout.write("🌱 جاري إضافة بيانات التقييم التجريبية...")

        # الحصول على جميع الكائنات
        zones = list(Zone.objects.all())
        natures = list(NatureImmeuble.objects.all())

        # نطاقات الأسعار التجريبية (دج/م²) حسب المنطقة
        price_ranges = {
            'residential': (30000, 80000),
            'city_center': (60000, 150000),
            'peripheral': (20000, 50000),
            'remote': (8000, 25000),
        }

        # معاملات حسب طبيعة العقار (بدون coefficient)
        nature_multipliers = {
            'individuels': 1.2,
            'collectifs': 1.0,
            'locaux_commerciaux': 1.8,
            'hangars': 0.8,
            'terrains_nus': 0.6,
            'terrains_plaine': 0.4,
            'terrains_pente': 0.3,
        }

        created_count = 0
        skipped_count = 0

        # أخذ عينة من الولايات والبلديات
        wilayas = Wilaya.objects.all()[:15]

        for wilaya in wilayas:
            communes = Commune.objects.filter(wilaya=wilaya)[:4]

            for commune in communes:
                for zone in zones:
                    zone_key = zone.key
                    base_min, base_max = price_ranges.get(zone_key, (20000, 60000))

                    for nature in natures:
                        nature_key = nature.key
                        multiplier = nature_multipliers.get(nature_key, 1.0)

                        # تعديل السعر حسب المنطقة والولاية
                        wilaya_factor = 0.8 + (int(wilaya.code) / 100)
                        adjusted_min = int(base_min * multiplier * wilaya_factor)
                        adjusted_max = int(base_max * multiplier * wilaya_factor)

                        # الحصول على خصائص هذه الطبيعة
                        caracteristiques = Caracteristique.objects.filter(nature=nature)

                        for carac in caracteristiques:
                            # إضافة تباين عشوائي للخصائص المختلفة
                            carac_variation = {
                                'standing': 1.3,
                                'ameliore': 1.1,
                                'economique': 0.9,
                                'precaire': 0.7,
                                'artere_haute': 1.4,
                                'artere_moyen': 1.0,
                                'artere_faible': 0.8,
                                'zone_urbaine': 1.0,
                                'zone_rurale': 0.7,
                                'pp_2f_avec': 1.2,
                                'pp_1f_avec': 1.0,
                                'pp_2f_sans': 0.9,
                                'pp_1f_sans': 0.8,
                                'indivision': 0.7,
                                'industriel': 1.1,
                                'potentialite_elevee': 1.3,
                                'potentialite_moyenne': 1.0,
                                'potentialite_faible': 0.8,
                            }

                            carac_factor = carac_variation.get(carac.key, 1.0)

                            final_min = int(adjusted_min * carac_factor)
                            final_max = int(adjusted_max * carac_factor)

                            # التأكد من أن min < max
                            if final_min > final_max:
                                final_min, final_max = final_max, final_min

                            # إنشاء نطاق التقييم
                            try:
                                obj, created = ValuationRange.objects.update_or_create(
                                    wilaya=wilaya,
                                    commune=commune,
                                    zone=zone,
                                    nature=nature,
                                    caracteristique=carac,
                                    defaults={
                                        'min_price_per_sqm': final_min,
                                        'max_price_per_sqm': final_max,
                                        'notes': f'بيانات تجريبية - {zone.name_ar} - {nature.name_ar}'
                                    }
                                )
                                if created:
                                    created_count += 1
                            except Exception as e:
                                self.stdout.write(self.style.WARNING(
                                    f"⚠️ خطأ في {wilaya.name_ar}/{commune.name_ar}/{carac.name_ar}: {e}"))
                                skipped_count += 1

        self.stdout.write(self.style.SUCCESS(
            f"✅ تم إضافة {created_count} نطاق تقييم، تخطي {skipped_count}"
        ))
        self.stdout.write(self.style.SUCCESS("🎉 اكتمل إضافة البيانات التجريبية!"))