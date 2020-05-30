import sqlite3
import apu
import telegram


def start(update, context):
    apu.botM(update, context,
             ":D")


def help(update, context):
    apu.botM(update, context,
             "/uusi komennolla voit lisätä uusia pelaajia tietokantaan. "
             "Oletuksena uudet pelaajat eivät ole maksaneet liiga-maksua.\n"
             "(esim. /uusi Timppa, Tomppa)\n\n"
             "/maksu komennolla voit päivittää henkilön liiga-maksun tilan.\n"
             "(esim. /maksu Timppa, Tomppa)\n\n"
             "/kroke komennolla voit lisätä kyseisen päivän tietokantaan.\n"
             "(esim. /kroke)\n\n"
             "/sijoitus komennolla voit lisätä pelaajille sijotuksen "
             "osakilpailussa. Jotta sijoituksen voi lisätä, on kyseinen päivä "
             "oltava lisätty aiemmin /kroke komennolla. Lisäksi pelaajien on "
             "löydyttävä tietokannasta.\n"
             "(esim. /sijoitus 2, Timppa, Tomppa)\n\n"
             "/tulokset komennolla voit tarkastella sijoituksia kesäliigassa. "
             "Jos komennon ajaa ilman parametrejä, listaa se kymmenen parhaiten "
             "menestynyttä pelaajaa. Jos parametriksi antaa yhden pelaajan "
             "nimen, listaa se kaikki kyseisen pelaajan sijoitukset kaikista "
             "kaikista osakilpailuista.\n"
             "(esim. /tulokset)\n"
             "(esim. /tulokset Timppa)")


def uusi(update, context):
    user = update.effective_user.id
    if not apu.permit(user):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Sinulla ei ole oikeuksia lisätä uusia "
                                      "henkilöitä tietokantaan")
        return
    names = apu.names(context.args)
    conn = sqlite3.connect(apu.db_path)
    cursor = conn.cursor()
    ins = """
        INSERT INTO Maksut
        SELECT ?, ?
        WHERE NOT EXISTS(SELECT 1 FROM Maksut WHERE nimi = ?)
    """
    for name in names:
        cursor.execute(ins, (name, 0, name))
    conn.commit()
    conn.close()
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Henkilö(t) lisätty onnistuneesti "
                             "tietokantaan")


def maksu(update, context):
    user = update.effective_user.id
    if not apu.permit(user):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Sinulla ei ole oikeuksia lisätä uusia "
                                 "henkilöitä tietokantaan")
        return
    names = apu.names(context.args)
    conn = sqlite3.connect(apu.db_path)
    cursor = conn.cursor()
    sel = """
        SELECT *
        FROM Maksut
        WHERE nimi = ?
    """
    ins = """
        INSERT INTO Maksut
        VALUES(?, ?)
    """
    for name in names:
        cursor.execute(sel, (name,))
        rows = cursor.fetchall()
        if len(rows) == 0:
            cursor.execute(ins, (name, 0))
    upd = """
        UPDATE Maksut
        SET maksu = 1
        WHERE nimi = ?
    """
    for name in names:
        cursor.execute(upd, (name,))
    conn.commit()
    conn.close()
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Henkilö(t) on merkitty maksaneeksi")


def kroke(update, context):
    user = update.effective_user.id
    if not apu.permit(user):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Sinulla ei ole oikeuksia lisätä uusia "
                                      "osakilpailuita.")
        return
    date = update.message.date
    conn = sqlite3.connect(apu.db_path)
    cursor = conn.cursor()
    ins = """
        INSERT INTO Kroket
        SELECT ?, ?
        WHERE NOT EXISTS(SELECT 1 FROM Kroket WHERE pv = ? AND kuu = ?)
    """
    cursor.execute(ins, (date.day, date.month, date.day, date.month))
    conn.commit()
    conn.close()
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text="Osakilpailu lisätty tietokantaan")


def sijoitus(update, context):
    user = update.effective_user.id
    if not apu.permit(user):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Sinulla ei ole oikeuksia lisätä uusia "
                                 "henkilöitä tietokantaan")
        return
    names = apu.names(context.args)
    if len(names) < 2 or (not names[0].isdigit() and int(names[0]) in range(1, 10)):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Anna ensimmäisenä parametrinä sijoitus "
                                 "ja tämän jälkeen henkilöt jotka saavuttivat "
                                 "kyseisen sijan. Ertota parametrit pilkulla.")
        return
    place = int(names[0])
    points = apu.switch(place)
    names = names[1:]
    date = update.message.date
    conn = sqlite3.connect(apu.db_path)
    cursor = conn.cursor()
    sel = """
        SELECT *
        FROM Tapahtumat
        WHERE ukko = ? AND pv = ? AND kuu = ?
    """
    sel2 = """
        SELECT *
        FROM Kroket
        WHERE pv = ? AND kuu = ?
    """
    cursor.execute(sel2, (date.day, date.month))
    rows = cursor.fetchall()
    if len(rows) == 0:
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Tälle päivälle ei ole tallennettu"
                                 "osakilpailua. Komennolla /kroke voit lisätä"
                                 "tälle päivälle osakilpailun.")
        conn.close()
        return
    added = []
    notadded = []
    for name in names:
        cursor.execute(sel, (name, date.day, date.month))
        rows = cursor.fetchall()
        if len(rows) == 0:
            apu.piste(update, context, name, points)
            added.append(name)
        else:
            notadded.append(name)
    conn.close()
    if len(notadded) == 0:
        apu.botM(update, context,
                 "Pisteet lisätty onnistuneesti pelaajille.")
    elif len(added) == 0:
        apu.botM(update, context,
                 "Kaikille pelaajille oli jo lisätty pisteet.")
    else:
        apu.botM(update, context, "Pelaajille {} lisätty pisteet. Pelaajille"
                 " {} oli jo lisätty pisteet.".format(added, notadded))


def tulokset(update, context):
    names = apu.names(context.args)
    if len(names) > 1:
        apu.botM(update, context,
                 "Jos annat parametrinä yhden nimen, palauttaa komento kyseisen "
                 "henkilön tulokset kaikissa osakilpailuissa. Jos taas et anna "
                 "yhtään parametria, palauttaa komento parhaiten menestyneet "
                 "pelaajat ja heidän kokonaispistemäärät.")
        return
    conn = sqlite3.connect(apu.db_path)
    cursor = conn.cursor()
    if names[0] == '':
        sel = """
            SELECT nimi, maksu, SUM(pisteet) AS pisteet
            FROM Maksut, Tapahtumat
            WHERE nimi = ukko
            GROUP BY nimi
            ORDER BY -SUM(pisteet)
            LIMIT 10
        """
        cursor.execute(sel)
        rows = cursor.fetchall()
        conn.close()
        res = """```
Kymmenen parasta pelaajaa:
==========================
Pisteet Maksu Nimi
"""
        for r in rows:
            p = r[2]
            if p < 10:
                p = str(p) + " "
            res = res + """
{}      {}     {}""".format(p, r[1], r[0])
        res = res + "```"
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=res,
                                 parse_mode=telegram.ParseMode.MARKDOWN)
    else:
        conn = sqlite3.connect(apu.db_path)
        cursor = conn.cursor()
        sel1 = """
            SELECT *
            FROM Maksut
            WHERE nimi = ?
        """
        cursor.execute(sel1, (names[0],))
        rows = cursor.fetchall()
        if len(rows) == 0:
            apu.botM(update, context,
                     "Kyseistä henkilöä ei ole vielä lisätty tietokantaan")
            conn.close()
            return
        sel = """
            SELECT *
            FROM Tapahtumat
            WHERE ukko = ?
            ORDER BY kuu, pv
        """
        cursor.execute(sel, (names[0],))
        rows = cursor.fetchall()
        conn.close()
        res = """```
Pelaajan sijoittumiset:
=======================
Pvm    Pisteet
"""
        for r in rows:
            p = str(r[2])
            if r[1] < 10:
                p = p + " "
            pvm = "{}.{}".format(r[1], p)
            res = res + """
{}   {}""".format(pvm, r[3])
        res = res + "```"
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text=res,
                                 parse_mode=telegram.ParseMode.MARKDOWN)
