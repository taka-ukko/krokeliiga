from telegram.ext import (Updater, CommandHandler, ConversationHandler, MessageHandler, Filters)
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
import logging
import sqlite3

db_path = r"C:\Users\veikk\projektit\krokeliiga\tilastot.db"
logging.basicConfig(format="""%(asctime)s - %(name)s - %(levelname)s -
                    %(message)s""",
                    level=logging.INFO)
custom = [['Ensimmäinen', 'Toinen'], ['Kolmas', 'Pääsi maaliin'], ['Peruuta']]
markup = ReplyKeyboardMarkup(custom, one_time_keyboard=True,
                             resize_keyboard=True)
SCORES = range(1)


def permit(id: int):
    with open(r'C:\Users\veikk\projektit\krokeliiga\luvat.txt', 'r') as permissions:
        if str(id) in permissions.read():
            return True
        else:
            return False


def get_token():
    with open(r'C:\Users\veikk\projektit\krokeliiga\token.txt', 'r') as token_file:
        token = token_file.readlines()[0].strip(" \n")
    return token


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=""":D""")


def uusi(update, context):
    user = update.effective_user.id
    if not permit(user):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="""Sinulla ei ole oikeuksia lisätä uusia henkilöitä tietokantaan""")
        return
    arguments = context.args
    if not len(arguments) == 1:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="""Kirjoita henkilön nimi kommennon jälkeen välillä erotettuna. Nimi saa koostu ainoastaan yhdestä osasta.""")
        return
    name = arguments[0]
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    ins = """
        INSERT INTO Maksut
        VALUES(?, ?)
    """
    cursor.execute(ins, (name, 0))
    conn.commit()
    conn.close()
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="""Henkilö lisätty onnistuneesti tietokantaan""")


def maksu(update, context):
    user = update.effective_user.id
    if not permit(user):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="""Sinulla ei ole oikeuksia lisätä uusia henkilöitä tietokantaan""")
        return
    arguments = context.args
    if not len(arguments) == 1:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="""Kirjoita henkilön nimi kommennon jälkeen välillä erotettuna""")
        return
    name = arguments[0]
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    sel = """
        SELECT *
        FROM Maksut
        WHERE nimi = ?
    """
    cursor.execute(sel, (name,))
    rows = cursor.fetchall()
    if len(rows) == 0:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="""Tätä henkilöä ei ole vielä lisätty tietokantaan""")
        return
    upd = """
        UPDATE Maksut
        SET maksu = 1
        WHERE nimi = ?
    """
    cursor.execute(upd, (name,))
    conn.commit()
    conn.close()
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="""Henkilö on merkitty maksaneeksi""")


def sijoitus(update, context):
    user = update.effective_user.id
    if not permit(user):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="""Sinulla ei ole oikeuksia lisätä uusia henkilöitä tietokantaan""")
        return
    arguments = context.args
    if not len(arguments) == 1:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="""Kirjoita henkilön nimi kommennon jälkeen välillä erotettuna""")
        return
    name = arguments[0]
    date = update.message.date
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    sel = """
        SELECT *
        FROM Tapahtumat
        WHERE ukko = ? AND pv = ? AND kuu = ?
    """
    cursor.execute(sel, (name, date.day, date.month))
    rows = cursor.fetchall()
    if not len(rows) == 0:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="""Henkilölle on jo lisätty pisteet tästä pelistä""")
        return
    context.user_data["name"] = name
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="""Valitse sijoitus henkilölle""",
                             reply_markup=markup)
    return SCORES


def piste(update, context, pisteet: int):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    ins = """
        INSERT INTO Tapahtumat
        VALUES (?, ?, ?, ?)
    """
    date = update.message.date
    cursor.execute(ins, (context.user_data.get("name"), date.day, date.month, pisteet))
    conn.commit()
    conn.close()
    context.user_data["name"] = ""


def eka(update, context):
    piste(update, context, 4)
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="""Pisteet lisätty onnistuneesti""")
    return ConversationHandler.END


def toka(update, context):
    piste(update, context, 3)
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="""Pisteet lisätty onnistuneesti""",
                             reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def kolmas(update, context):
    piste(update, context, 2)
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="""Pisteet lisätty onnistuneesti""",
                             reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def muu(update, context):
    piste(update, context, 1)
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="""Pisteet lisätty onnistuneesti""",
                             reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def peruuta(update, context):
    context.user_data["name"] = ""
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="""Pisteiden lisäys peruutettu""",
                             reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END


def main():
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
    conn.commit()
    conn.close()
    updater = Updater(token=get_token(), use_context=True)
    dispatcher = updater.dispatcher
    # handlers
    start_handler = CommandHandler('start', start)
    uusi_handler = CommandHandler('uusi', uusi)
    maksu_handler = CommandHandler('maksu', maksu)
    sij_handler = ConversationHandler(
        entry_points=[CommandHandler("sijoitus", sijoitus)],
        states={
            SCORES: [MessageHandler(Filters.regex('^(Ensimmäinen)$'), eka),
                     MessageHandler(Filters.regex('^(Toinen)$'), toka),
                     MessageHandler(Filters.regex('^(Kolmas)$'), kolmas),
                     MessageHandler(Filters.regex('^(Pääsi maaliin)$'), muu)]
        },
        fallbacks=[MessageHandler(Filters.regex('^(Peruuta)$'), peruuta)]
    )
    # handlers to dispatchers
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(uusi_handler)
    dispatcher.add_handler(maksu_handler)
    dispatcher.add_handler(sij_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
