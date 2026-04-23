import pymysql
import os
from datetime import datetime

def backup_manual():
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="controletelefonepmp"
    )
    cursor = conn.cursor()

    # Pasta do backup
    backup_dir = r"F:\CI-Manutencao\Mateus\BACKUP"
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    # Nome do arquivo
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(backup_dir, f"backup_manual_{now}.sql")

    with open(backup_file, "w", encoding="utf-8") as f:
        cursor.execute("SHOW TABLES")
        tables = [t[0] for t in cursor.fetchall()]

        for table in tables:
            cursor.execute(f"SHOW CREATE TABLE {table}")
            create_table = cursor.fetchone()[1]
            f.write(f"{create_table};\n\n")

            cursor.execute(f"SELECT * FROM {table}")
            rows = cursor.fetchall()

            for row in rows:
                values = ', '.join([f"'{str(v).replace('\'', '\\\'')}'" if v is not None else 'NULL' for v in row])
                f.write(f"INSERT INTO {table} VALUES ({values});\n")
            f.write("\n\n")

    cursor.close()
    conn.close()
    return backup_file

