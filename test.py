from sqlite3 import connect
from threading import Lock

lock = Lock()
con = connect("saves.db", check_same_thread=False)
cur = con.cursor()
try:
    lock.acquire(True)
    chat_ids = [int(x[0]) for x in cur.execute("""Select chat_id from users""").fetchall()]
finally:
    lock.release()
