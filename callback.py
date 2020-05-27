import sqlite3
import apu
from telegram import ReplyKeyboardRemove
from telegram.ext import ConversationHandler


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=""":D""")


def uusi(update, context):
    user = update.effective_user.id
    if not apu.permit(user):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="""Sinulla ei ole oikeuksia lisätä uusia henkilöitä tietokantaan""")
        return
    arguments = context.args
    if not len(arguments) == 1:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="""Kirjoita henkilön nimi kommennon jälkeen välillä erotettuna. Nimi saa koostu ainoastaan yhdestä osasta.""")
        return
    name = arguments[0]
    conn = sqlite3.connect(apu.db_path)
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
    if not apu.permit(user):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="""Sinulla ei ole oikeuksia lisätä uusia henkilöitä tietokantaan""")
        return
    arguments = context.args
    if not len(arguments) == 1:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="""Kirjoita henkilön nimi kommennon jälkeen välillä erotettuna""")
        return
    name = arguments[0]
    conn = sqlite3.connect(apu.db_path)
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
    if not apu.permit(user):
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
    conn = sqlite3.connect(apu.db_path)
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
                             reply_markup=apu.markup)
    return apu.SCORES


def piste(update, context, pisteet: int):
    conn = sqlite3.connect(apu.db_path)
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
