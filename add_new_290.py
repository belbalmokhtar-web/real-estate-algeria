# add_new_290.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from properties.models import PromoteurImmobilier
from properties.models_valuation import Wilaya

# قاموس الولايات
wilaya_map = {
    'TIZI OUZOU': Wilaya.objects.filter(name_ar='تيزي وزو').first(),
    'ALGER': Wilaya.objects.filter(name_ar='الجزائر').first(),
    'CONSTANTINE': Wilaya.objects.filter(name_ar='قسنطينة').first(),
    'ORAN': Wilaya.objects.filter(name_ar='وهران').first(),
    'SOUK AHRAS': Wilaya.objects.filter(name_ar='سوق أهراس').first(),
    'BATNA': Wilaya.objects.filter(name_ar='باتنة').first(),
    'SETIF': Wilaya.objects.filter(name_ar='سطيف').first(),
    'TIARET': Wilaya.objects.filter(name_ar='تيارت').first(),
    'BLIDA': Wilaya.objects.filter(name_ar='البليدة').first(),
    'BOUMERDES': Wilaya.objects.filter(name_ar='بومرداس').first(),
    'RELIZANE': Wilaya.objects.filter(name_ar='غليزان').first(),
    'BEJAIA': Wilaya.objects.filter(name_ar='بجاية').first(),
    'DJELFA': Wilaya.objects.filter(name_ar='الجلفة').first(),
    'MASCARA': Wilaya.objects.filter(name_ar='معسكر').first(),
    'AIN DEFLA': Wilaya.objects.filter(name_ar='عين الدفلى').first(),
    'GUELMA': Wilaya.objects.filter(name_ar='قالمة').first(),
    'CHLEF': Wilaya.objects.filter(name_ar='الشلف').first(),
    'S.B.ABBES': Wilaya.objects.filter(name_ar='سيدي بلعباس').first(),
    'MILA': Wilaya.objects.filter(name_ar='ميلة').first(),
    'TEBESSA': Wilaya.objects.filter(name_ar='تبسة').first(),
    'OUARGLA': Wilaya.objects.filter(name_ar='ورقلة').first(),
    'TISSEMSILT': Wilaya.objects.filter(name_ar='تيسمسيلت').first(),
    'O.E.BOUAGHI': Wilaya.objects.filter(name_ar='أم البواقي').first(),
    'EL TARF': Wilaya.objects.filter(name_ar='الطارف').first(),
    'MOSTAGANEM': Wilaya.objects.filter(name_ar='مستغانم').first(),
    'BISKRA': Wilaya.objects.filter(name_ar='بسكرة').first(),
    'ADRAR': Wilaya.objects.filter(name_ar='أدرار').first(),
    'LAGHOUAT': Wilaya.objects.filter(name_ar='الأغواط').first(),
    'TOUGGOURT': Wilaya.objects.filter(name_ar='تقرت').first(),
    'EL OUED': Wilaya.objects.filter(name_ar='الوادي').first(),
    'B.B.ARRERIDJ': Wilaya.objects.filter(name_ar='برج بوعريريج').first(),
    'BOUIRA': Wilaya.objects.filter(name_ar='البويرة').first(),
    'MEDEA': Wilaya.objects.filter(name_ar='المدية').first(),
    'TLEMCEN': Wilaya.objects.filter(name_ar='تلمسان').first(),
    'M SILA': Wilaya.objects.filter(name_ar='المسيلة').first(),
}

# قائمة المطورين الجدد (الأرقام الجديدة فقط)
new_promoteurs = [
    ("00618", "AIT AOUDIA FERHAT", "SARL NEW URBATIM CONCEPT",
     "Local N° 02 à Bord de la rue Ben Selma Ramdane, Lotissement Cité B lot D, Nouvelle Ville, Cne de Tizi Ouzou",
     "026 21 87 39", "TIZI OUZOU"),
    ("00619", "HAMMI HAMZA", "EURL CODEV CONSTRUCTION ET DEVELOPPEMENT",
     "Rue Lakhdar Menaa, Cité 19+2 logts Bt c AP A, Cne de Ben Aknoun", "021 94 64 60", "ALGER"),
    ("00620", "ALI KHODJA REDHA", "SARL NEXT ART", "Rue Maddaoui Boudjemaa N°57 Local N°02, Cne de Constantine",
     "031 88 44 44", "CONSTANTINE"),
    ("00621", "ADOUANE MOHAMED", "EURL BENABED PROMOTION IMMOBILIERE",
     "Lotissement 283 N° 301 Local N°04, Cne de Bir El Djir", "040 21 56 57", "ORAN"),
    # أضف باقي البيانات من الـ raw_entries أعلاه هنا
]

# إضافة المطورين
created = 0
exists = 0

for data in new_promoteurs:
    num, nom, gerant, adresse, tel, wilaya_name = data
    wilaya = wilaya_map.get(wilaya_name)

    if not PromoteurImmobilier.objects.filter(numero_affiliation=num).exists():
        PromoteurImmobilier.objects.create(
            numero_affiliation=num,
            nom_entreprise=nom,
            nom_gerant=gerant,
            adresse=adresse,
            telephone=tel,
            wilaya=wilaya,
        )
        created += 1
        print(f"✅ تم إضافة: {num} - {nom}")
    else:
        exists += 1

print(f"\n📊 النتائج:")
print(f"   ✅ تم إضافة {created} مطور جديد")
print(f"   ⚠️ موجود مسبقاً: {exists} مطور")
print(f"   📈 إجمالي المطورين الآن: {PromoteurImmobilier.objects.count()}")