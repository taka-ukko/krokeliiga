import sqlite3

db_path = r"C:\Users\veikk\projektit\krokeliiga\tilastot.db"
token_path = r'C:\Users\veikk\projektit\krokeliiga\token.txt'
perm_path = r'C:\Users\veikk\projektit\krokeliiga\luvat.txt'


def permit(id: int):
    with open(perm_path, 'r') as permissions:
        if str(id) in permissions.read():
            return True
        else:
            return False


def get_token():
    with open(token_path, 'r') as token_file:
        token = token_file.readlines()[0].strip(" \n")
    return token


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
        pv INT,
        kuu INT,
        pisteet INT,
        PRIMARY KEY (ukko, pv, kuu)
    )""")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Kroket (
        pv INT,
        kuu INT,
        PRIMARY KEY (pv, kuu)
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
        range(4, 10): 1
    }
    return switcher.get(placement)


def botM(update, context, message: str):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=message)


def piste(update, context, name: str, pisteet: int):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    ins = """
        INSERT INTO Tapahtumat
        VALUES (?, ?, ?, ?)
    """
    date = update.message.date
    cursor.execute(ins, (name, date.day, date.month, pisteet))
    conn.commit()
    conn.close()
