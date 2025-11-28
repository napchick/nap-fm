from sqlalchemy import create_engine
import os

from dotenv import load_dotenv
if os.path.exists(".env"):
    load_dotenv()

# url = 'postgresql+psycopg2://neondb_owner:npg_8e7UwjHYWzRa@ep-summer-queen-adz2anyx-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=verify-ca&sslrootcert=isrgrootx1.pem'



new_url = os.getenv("NEW_DATABASE_URL")
print(new_url)


engine = create_engine(new_url, pool_pre_ping=True)

try:
    with engine.connect() as conn:
        print("✅ Подключение установлено!")
except Exception as e:
    print("❌ Ошибка подключения:", e)
#  python database/test.py

# export OLD_DB_URL="postgresql+psycopg2://neondb_owner:npg_8e7UwjHYWzRa@ep-summer-queen-adz2anyx-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=verify-ca&sslrootcert=isrgrootx1.pem"
# pg_dump --format=custom --no-owner --no-acl "$OLD_DB_URL" -f backup.dump

# export NEW_DB_URL="postgresql+psycopg2://neondb_owner:npg_qyjBSL8N7Orn@ep-withered-recipe-a499k62v-pooler.us-east-1.aws.neon.tech/neondb?sslmode=verify-ca&sslrootcert=isrgrootx1.pem"
# pg_restore --no-owner --no-acl --clean --if-exists --dbname="$NEW_DB_URL" backup.dump
