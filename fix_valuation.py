import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from django.db import connection

def main():
    cursor = connection.cursor()
    cursor.execute('PRAGMA table_info(properties_valuation)')
    rows = cursor.fetchall()
    cols = [row[1] for row in rows]
    print('Current columns:', cols)
    has_min_val = 'min_value' in cols
    has_max_val = 'max_value' in cols
    has_min_new = 'min_price_per_sqm' in cols
    has_max_new = 'max_price_per_sqm' in cols
    print('min_value exists:', has_min_val)
    print('max_value exists:', has_max_val)
    print('min_price_per_sqm exists:', has_min_new)
    print('max_price_per_sqm exists:', has_max_new)

    if has_min_val and has_max_val:
        cursor.execute('ALTER TABLE properties_valuation RENAME COLUMN min_value TO min_price_per_sqm')
        cursor.execute('ALTER TABLE properties_valuation RENAME COLUMN max_value TO max_price_per_sqm')
        print('Renamed columns.')
    elif not has_min_new or not has_max_new:
        if not has_min_new:
            cursor.execute('ALTER TABLE properties_valuation ADD COLUMN min_price_per_sqm decimal(12,2)')
            print('Added min_price_per_sqm.')
        if not has_max_new:
            cursor.execute('ALTER TABLE properties_valuation ADD COLUMN max_price_per_sqm decimal(12,2)')
            print('Added max_price_per_sqm.')
    else:
        print('Columns already correct.')

if __name__ == "__main__":
    main()