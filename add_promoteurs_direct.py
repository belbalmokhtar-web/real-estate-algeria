# add_promoteurs_direct.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from properties.models import PromoteurImmobilier
from properties.models_valuation import Wilaya

# قاموس الولايات
wilaya_map = {
    'M SILA': Wilaya.objects.filter(name_ar='المسيلة').first(),
    'CONSTANTINE': Wilaya.objects.filter(name_ar='قسنطينة').first(),
    'DJELFA': Wilaya.objects.filter(name_ar='الجلفة').first(),
    'RELIZANE': Wilaya.objects.filter(name_ar='غليزان').first(),
    'BOUMERDES': Wilaya.objects.filter(name_ar='بومرداس').first(),
    'ALGER': Wilaya.objects.filter(name_ar='الجزائر').first(),
    'BEJAIA': Wilaya.objects.filter(name_ar='بجاية').first(),
    'SKIKDA': Wilaya.objects.filter(name_ar='سكيكدة').first(),
    'ANNABA': Wilaya.objects.filter(name_ar='عنابة').first(),
    'TIPAZA': Wilaya.objects.filter(name_ar='تيبازة').first(),
    'BATNA': Wilaya.objects.filter(name_ar='باتنة').first(),
    'TIZI OUZOU': Wilaya.objects.filter(name_ar='تيزي وزو').first(),
    'SAIDA': Wilaya.objects.filter(name_ar='سعيدة').first(),
    'MASCARA': Wilaya.objects.filter(name_ar='معسكر').first(),
    'CHLEF': Wilaya.objects.filter(name_ar='الشلف').first(),
    'S.B.ABBES': Wilaya.objects.filter(name_ar='سيدي بلعباس').first(),
    'GUELMA': Wilaya.objects.filter(name_ar='قالمة').first(),
    'A.TEMOUCHENT': Wilaya.objects.filter(name_ar='عين تيموشنت').first(),
    'AIN DEFLA': Wilaya.objects.filter(name_ar='عين الدفلى').first(),
    'B.B.ARRERIDJ': Wilaya.objects.filter(name_ar='برج بوعريريج').first(),
    'EL TARF': Wilaya.objects.filter(name_ar='الطارف').first(),
    'SOUK AHRAS': Wilaya.objects.filter(name_ar='سوق أهراس').first(),
    'O.E.BOUAGHI': Wilaya.objects.filter(name_ar='أم البواقي').first(),
    'OUARGLA': Wilaya.objects.filter(name_ar='ورقلة').first(),
    'GHARDAIA': Wilaya.objects.filter(name_ar='غرداية').first(),
    'JIJEL': Wilaya.objects.filter(name_ar='جيجل').first(),
    'BLIDA': Wilaya.objects.filter(name_ar='البليدة').first(),
    'BOUIRA': Wilaya.objects.filter(name_ar='البويرة').first(),
    'MEDEA': Wilaya.objects.filter(name_ar='المدية').first(),
    'TLEMCEN': Wilaya.objects.filter(name_ar='تلمسان').first(),
    'TEBESSA': Wilaya.objects.filter(name_ar='تبسة').first(),
    'TIARET': Wilaya.objects.filter(name_ar='تيارت').first(),
    'MILA': Wilaya.objects.filter(name_ar='ميلة').first(),
    'MOSTAGANEM': Wilaya.objects.filter(name_ar='مستغانم').first(),
    'ORAN': Wilaya.objects.filter(name_ar='وهران').first(),
    'SETIF': Wilaya.objects.filter(name_ar='سطيف').first(),
    'BISKRA': Wilaya.objects.filter(name_ar='بسكرة').first(),
    'TOUGGOURT': Wilaya.objects.filter(name_ar='تقرت').first(),
    'EL OUED': Wilaya.objects.filter(name_ar='الوادي').first(),
}

# بيانات المطورين (أول 20 نموذج - أضف الباقي من ملف add_500.py)
new_promoteurs = [
    ("00066", "DEGHICHE AMMAR", "DEGHICHE AMMAR",
     "Promotion immobiliere 39 Logts, Nouvelle zone urbaine Bt A1 N°02, Cne de M'Sila", "035 55 66 82", "M SILA"),
    ("00067", "TAHI YOUCEF", "TAHI YOUCEF", "Lotissement 290 Lot 04 N°01, Cne de M'Sila", "035 59 75 58", "M SILA"),
    ("00070", "LARKEM RIAD", "EURL ESSAFIA ETUDE ET REALISATION",
     "Cité 600 logts, Ain El Bey, Bt 22 N°82, Cne de Constantine", "031 90 49 33", "CONSTANTINE"),
    ("00071", "TOUMI KOUIDER", "TOUMI KOUIDER", "Cité Ben Djerma Bt 361 N°11B Section 152, Cne de Djelfa", "",
     "DJELFA"),
    ("00074", "MOKHTARI MOHAMMED Ben Bouabdellah", "MOKHTARI MOHAMMED Ben Bouabdellah",
     "Boulevard des martyres local N°03 sidi mohamed Benali, Cne de Relizane", "046 94 15 39", "RELIZANE"),
    ("00075", "BOUDJEMIA ABDELGHANI", "EURL INNOVATIVE PROMOTION IMMOBILIERE",
     "Cité 392 lgts BT N°23 entrée T N°03, Cne de Boumerdes", "024 79 70 20", "BOUMERDES"),
    ("00076", "BENRAGOUBA NOUR EDDINE", "EURL PROMOTION IMMOBILIERE HOURIATE EL SALEM",
     "Cité 602 Lgts BT 11 Lot N°282, Cne de Chéraga", "023 37 27 64", "ALGER"),
    ("00077", "SADJI AHMED", "EURL PROSAD", "Rue des frères Ouyougout N°01, Cne de Béjaïa", "034 12 81 52", "BEJAIA"),
    ("00080", "ALIDRA ABDELWAHAB", "ALIDRA ABDELWAHAB",
     "Cite 30 lgts LSP Cite des freres Saker BT N°01 local N° 01, Cne de Skikda", "", "SKIKDA"),
    ("00081", "KHELLAIFIA SABRI ADEL", "SARL ARABE REAL ESTATE", "Cité Gassiot 02, Villa N° 01, Cne de Annaba",
     "038 86 00 05", "ANNABA"),
    ("00083", "CHAIB EDDOUIR CHAREF", "CHAIB EDDOUIR CHAREF", "Cité Kassass Mohammed, Cne de Oued Rhiou", "",
     "RELIZANE"),
    ("00085", "DJAMA SAMIR", "EURL ERIDJ", "Résidence El Hadhaba Section 02 Ilot 892 Bt ABC Local N55C, Cne de Chéraga",
     "034 22 92 85", "ALGER"),
    ("00087", "KHALED HACENE", "KHALED HACENE", "Cité Ain Ennaadja lot n° 04 local n° 11, Cne de Djasr Kasentina",
     "023 59 20 77", "ALGER"),
    ("00088", "HANITSER DJILLALI", "HANITSER DJILLALI", "Lotissement 128 N°25 El Mohgan, Cne de Arzew", "040 22 65 80",
     "ORAN"),
    ("00089", "OULAHBIB TARIK", "EURL AMENAGEMENT ET PROMOTION IMMOBILIERE (API)",
     "N°25 lotissement 110 parcelle A 1er étage, Cne de Bir El Djir", "041 428422", "ORAN"),
    ("00090", "BENBATOUCHE ABDELMOUTALEB", "BENBATOUCHE ABDELMOUTALEB", "Rue 1er Novembre, Cne de Barika",
     "033 89 47 48", "BATNA"),
    ("00091", "AMARI M'HAND", "SARL ISSUMAR PROMOTION IMMOBILIERE",
     "Lieu dit Ighil Ouazzoug Ilot 62 section 165, Cne de Béjaïa", "", "BEJAIA"),
    ("00094", "ZADI BELKACEM", "ZADI BELKACEM", "Projet 72 logts, Local N° 08 Bt2 entrée 02, Cne de Ben Mehidi", "",
     "EL TARF"),
    ("00095", "BOUAMARA ATMANE", "BOUAMARA ATMANE",
     "Cité Nouvelle Mosquée, section 154 propriété 125, Cne de Had-Sahary", "027 93 72 11", "DJELFA"),
    ("00096", "LALLALI MUSTAPHA", "LALLALI MUSTAPHA", "12 Rue des Frères Braci, Cne de Saïda", "048 47 80 49", "SAIDA"),
]

# إضافة المطورين
created = 0
exists = 0

for data in new_promoteurs:
    num, nom, gerant, adresse, tel, wilaya_name = data
    wilaya = wilaya_map.get(wilaya_name)

    # التحقق إذا كان المطور موجوداً
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
        print(f"⚠️ موجود بالفعل: {num} - {nom}")

print(f"\n📊 النتائج:")
print(f"   - تم إضافة {created} مطور جديد")
print(f"   - موجود مسبقاً: {exists} مطور")
print(f"   - إجمالي المطورين الآن: {PromoteurImmobilier.objects.count()}")