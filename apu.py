import sqlite3
from os import path
import urllib.request


pa = path.dirname(path.abspath(__file__))
perm_path = path.join(pa, "files", "luvat.txt")
db_path = path.join(pa, "files", "tilastot.db")
log_path = path.join(pa, "files", "krokebot.log")


def check_internet():
    url = "http://www.google.com/"
    try:
        urllib.request.urlopen(url)
        print("Connection succesful")
        return True
    except (urllib.error.URLError):
        print("No internet connection")
        return False


def permit(id: int):
    with open(perm_path, 'r') as permissions:
        if str(id) in permissions.read():
            return True
        else:
            return False


def tables():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Maksut (
        nimi CHAR(64),
        maksu INT DEFAULT 0,
        PRIMARY KEY (nimi)
    )""")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Tapahtumat (
        ukko CHAR(64),
        pvm CHAR(4),
        pisteet INT,
        PRIMARY KEY (ukko, pvm)
    )""")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Kroket (
        pvm CHAR(4),
        PRIMARY KEY (pvm)
    )""")
    conn.commit()
    conn.close()


def names(args: list):
    joined = ' '.join(args)
    names = joined.split(",")
    for i in range(len(names)):
        names[i] = names[i].strip()
    return names


def switch(placement: int):
    switcher = {
        1: 4,
        2: 3,
        3: 2,
        4: 1,
        5: 1,
        6: 1,
        7: 1,
        8: 1,
        9: 1,
    }
    return switcher.get(placement)


def botM(update, context, message: str):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=message)


def piste(update, context, name: str, pisteet: int, pvm: str):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    ins = """
        INSERT INTO Tapahtumat
        VALUES (?, ?, ?)
    """
    cursor.execute(ins, (name, pvm, pisteet))
    conn.commit()
    conn.close()


def fdate(kuu: str, pv: str):
    if len(pv) == 1:
        pv = "0" + pv
    if len(kuu) == 1:
        kuu = "0" + kuu
    return kuu + pv
