

from src.data.connection import get_connection
conn = get_connection()
print("connected:" ,conn.is_connected())
conn.close