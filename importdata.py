import pandas as pd
import psycopg2
import glob
import os

1. CONNECTING TO DATABASE
conn = psycopg2.connect("postgresql://neondb_owner:npg_3BMQWL1KzyCD@ep-nameless-unit-an8ghehu.c-6.us-east-1.aws.neon.tech/neondb?sslmode=require")
cursor = conn.cursor()

#2. DATASET FOLDER
dataset_folder = r"C:\Users\ASHOK\dataset"

#3. FIND ALL FILES (.xls + .ods)
file_patterns = ["*.xls", "*.ods"]
all_files = []

for pattern in file_patterns:
    all_files.extend(glob.glob(os.path.join(dataset_folder, pattern)))

print(f"Found {len(all_files)} files. Starting import...\n")

# 4. EXTRACT STATE NAME FROM FILENAME
def get_state_from_filename(filename):
    try:
        name = filename.split("_", 3)[-1]   # HIMACHAL_PRADESH.xls
        name = os.path.splitext(name)[0]    # remove extension
        return name.replace("_", " ").title()
    except:
        return "Unknown"

#5. LOOP FILES
for file_path in all_files:
    filename = os.path.basename(file_path)
    print(f"Processing: {filename}")

    state_name = get_state_from_filename(filename)

    ext = os.path.splitext(file_path)[1].lower()

    #READ FILE
    try:
        if ext == ".xls":
            df = pd.read_excel(file_path, engine='xlrd')
        elif ext == ".ods":
            df = pd.read_excel(file_path, engine='odf')
        else:
            print(f"⚠️ Skipping unsupported file: {filename}")
            continue
    except Exception as e:
        print(f"Error reading {filename}: {e}")
        continue

    print(f"Rows: {len(df)}")

    #INSERT DATA
    for _, row in df.iterrows():
        try:
            code = str(row.get('MDDS STC', '')).strip()
            name = row.get('STATE NAME', state_name)

            if not code:
                continue

            cursor.execute("""
                INSERT INTO "State" (name, code, "countryId")
                VALUES (%s, %s, 1)
                ON CONFLICT (code) DO NOTHING
            """, (name, code))

        except Exception as e:
            print(f"Insert error: {e}")
            conn.rollback()   #prevents crash
            continue

    print(f"Done: {state_name}\n")

# 6. SAVE + CLOSE
conn.commit()
cursor.close()
conn.close()

print("ALL DATA IMPORTED SUCCESSFULLY!")