# add_remaining_fixed.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from properties.models import PromoteurImmobilier
from properties.models_valuation import Wilaya

# ============================================================
# قاموس الولايات - تم إضافة جميع الولايات المفقودة
# ============================================================
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
    # ✅ الولايات المفقودة التي تسببت في الأخطاء
    'SKIKDA': Wilaya.objects.filter(name_ar='سكيكدة').first(),
    'ANNABA': Wilaya.objects.filter(name_ar='عنابة').first(),
    'JIJEL': Wilaya.objects.filter(name_ar='جيجل').first(),
    'TIPAZA': Wilaya.objects.filter(name_ar='تيبازة').first(),
    'SAIDA': Wilaya.objects.filter(name_ar='سعيدة').first(),
    'GHARDAIA': Wilaya.objects.filter(name_ar='غرداية').first(),
    'ILLIZI': Wilaya.objects.filter(name_ar='إليزي').first(),
    'BECHAR': Wilaya.objects.filter(name_ar='بشار').first(),
    'TAMANRASSET': Wilaya.objects.filter(name_ar='تمنراست').first(),
    'NAAMA': Wilaya.objects.filter(name_ar='النعامة').first(),
    'A.TEMOUCHENT': Wilaya.objects.filter(name_ar='عين تيموشنت').first(),
    'EL TARF': Wilaya.objects.filter(name_ar='الطارف').first(),
}

# ============================================================
# قائمة المطورين الذين تم تخطيهم بسبب أخطاء الولايات
# ============================================================
skipped_promoteurs = [
    ("00633", "BOURENDOUS ALI", "SARL PROMO IREAL", "Auto construction, Cne de Hamadi Krouma", "038 75 79 51",
     "SKIKDA"),
    ("00634", "GUERZA ABDELHAFID", "EURL GUERZA TRAVSKI", "Rue de citernes, Villa N° 01, Cne de Skikda", "030 92 13 98",
     "SKIKDA"),
    ("00655", "KHEZAZNA SOUHAIL", "SARL SAMA MARINA", "Cité 42 logts Villa N° 19, Cne de El Bouni", "", "ANNABA"),
    ("00671", "TABNI FERHAT", "TABNI FERHAT", "Projet 20 logts LSP Bt A Local 05 et 06, Cne de Ramdane Djamel", "",
     "SKIKDA"),
    ("00703", "DAOUDI FAYCAL", "SARL PROMOTION IMMOBILIERE LABBACI OURAILLA",
     "Champ de mars lot 21, local 04, Cne de Annaba", "038 44 58 87", "ANNABA"),
    ("00711", "GHERARI MOHAMED ISSAM", "GHERARI MOHAMED ISSAM",
     "Plage Rizi omar Hyppone promotion, Bt B N°103, Cne de Annaba", "", "ANNABA"),
    ("00735", "HADIDI AHCEN", "HADIDI AHCEN", "Cité plaine ouest 08 mars B, Lot N°13, Cne de Annaba", "038 43 89 98",
     "ANNABA"),
    ("00749", "SAHRAOUI LYDIA", "EURL BAT", "Boulevard Colonel lamouri Abdelkader N°01, Cne de Annaba", "038 83 80 64",
     "ANNABA"),
    ("00819", "RAMOUL MONCEF", "SARL ENNAJAH", "Hai 05 Juillet 1962, RDC, Cne de Annaba", "", "ANNABA"),
    ("00829", "AMIRI MILOUD", "AMIRI MILOUD", "N°09 Bt 01 Bloc A 1ere étage, Résidence 16 logements, Cne de El Bouni",
     "035 59 23 21", "ANNABA"),
    ("00839", "CHORFI OUAHID", "CHORFI OUAHID", "Lot N°01, Chentata Rez de chaussée Bt E N°01, Cne de Annaba",
     "038 84 12 55", "ANNABA"),
    ("00841", "DIABI ALI", "EURL NASSIM PROMOTION IMMOBILIERE",
     "Lieu dit Boukhadra (Bidari) N°07 Section 81, Cne de El Bouni", "", "ANNABA"),
    ("00842", "MEKIDECHE MOURAD", "SARL EL HANA CONSTRUCTION IMMOBILIERE",
     "N°02 Boulevard Decteur Tidi, 2ème étage N°205 et 206, Cne de Annaba", "", "ANNABA"),
    ("00850", "TALBI NABIL", "SARL MARSA EL ZITOUNE TCE", "N° 01 Rue de l'avant port, Cne de Annaba", "038 86 99 87",
     "ANNABA"),
    ("00864", "BENSADOK ALA EDDINE", "EURL KHEZAZNA KHALED", "Cité 900 Logts, N° 02 1er étage, Cne de El Bouni", "",
     "ANNABA"),
    ("00920", "BENTORKI MOHAMED HAKIM", "EURL BMH PROMO", "Place Mars N°12 Lotissement 42 Lots, Cne de Annaba",
     "038 43 14 75", "ANNABA"),
    ("00959", "TABNI IMAD", "TABNI IMAD", "Mafraza N° 02, Ramdane Djamel", "", "SKIKDA"),
    ("00978", "AOUED MOHAMED RIDA", "AOUED MOHAMED RIDA",
     "Lotissement 02 Cité Bouglouf Mabrouk N°01 RDC, Cne de Ramdane Djamel", "", "SKIKDA"),
    ("00990", "BOUHEMILA NADIR", "EURL PROMOTION IMMOBILIERE LYRIA",
     "Cite Rym 116 Logts N° 4 Cne De Annaba, Cne de Annaba", "038 86 13 27", "ANNABA"),
    ("00991", "NEHAL YACINE", "NEHAL YACINE", "Cité 80 logts 08 mars Bloc 2 N°10, Cne de Annaba", "", "ANNABA"),
    ("00995", "AWGRFU ANNABA", "AWGRFU ANNABA", "Rue Mustapha Ben Boulaid N°10 Bis, Cne de Annaba", "038 86 53 42",
     "ANNABA"),
    ("00873", "BAAZIZ BACHIR EDDINE", "EURL ARCHICOL", "Rue Didouche Mourad, Cne de Collo", "038 71 86 25", "SKIKDA"),
]

# ============================================================
# إضافة المطورين الذين تم تخطيهم
# ============================================================
print("=" * 60)
print("🚀 بدء إضافة المطورين الذين تم تخطيهم سابقاً...")
print("=" * 60)

created = 0
exists = 0
errors = 0

for data in skipped_promoteurs:
    num, nom, gerant, adresse, tel, wilaya_name = data
    wilaya = wilaya_map.get(wilaya_name)

    if not wilaya:
        errors += 1
        print(f"⚠️ لا تزال الولاية غير معروفة: '{wilaya_name}' للمطور {num}")
        continue

    if not PromoteurImmobilier.objects.filter(numero_affiliation=num).exists():
        try:
            PromoteurImmobilier.objects.create(
                numero_affiliation=num,
                nom_entreprise=nom[:255] if nom else "",
                nom_gerant=gerant[:255] if gerant else "",
                adresse=adresse[:500] if adresse else "",
                telephone=tel[:50] if tel else "",
                wilaya=wilaya,
            )
            created += 1
            print(f"✅ تم إضافة: {num} - {nom} ({wilaya_name})")
        except Exception as e:
            errors += 1
            print(f"❌ خطأ في إضافة المطور {num}: {e}")
    else:
        exists += 1
        print(f"⚠️ موجود مسبقاً: {num} - {nom}")

print("=" * 60)
print("📊 النتائج النهائية:")
print(f"   ✅ تم إضافة {created} مطور جديد")
print(f"   ⚠️ موجود مسبقاً: {exists} مطور")
print(f"   ❌ أخطاء/تخطي: {errors} سجل")
print(f"   📈 إجمالي المطورين الآن: {PromoteurImmobilier.objects.count()}")
print("=" * 60)