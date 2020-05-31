import sqlite3
import apu
import telegram
from emoji import emojize
import random


# -----------------------------------START--------------------------------------
def start(update, context):
    apu.botM(update, context,
             "Olen botti, joka ylläpitää konklaavin kesäliigan tietokantaa. "
             "/help komennolla saat listauksen käytössä olevista komennoista.")


# -----------------------------------HELP---------------------------------------
def help(update, context):
    no = emojize(":skull_and_crossbones:", use_aliases=True)
    yes = emojize(":yum:", use_aliases=True)
    apu.botM(update, context,
             "Komennot jotka eivät vaadi lupaa {}\n\n"  # ------------
             "/tulokset komennolla voit tarkastella sijoituksia kesäliigassa. "
             "Jos komennon ajaa ilman parametrejä, listaa se kymmenen parhaiten "
             "menestynyttä pelaajaa. Jos parametriksi antaa yhden pelaajan "
             "nimen, listaa se kaikki kyseisen pelaajan sijoitukset kaikista "
             "kaikista osakilpailuista.\n"
             "(esim. /tulokset)\n"
             "(esim. /tulokset Timppa)\n\n"
             "/pelaajat komennolla voit listata kaikki pelaajat, jotka on "
             "lisätty tietokantaan. Lisäksi tieto pelaajien liigamaksusta on "
             "listattu.\n"
             "(esim. /pelaajat)\n\n"
             "/joukkueet komennolla voit arpoa joukkuuet. Anna ensimmäiseksi "
             "parametriksi joukkueiden lukumäärä ja sen jälkeen pelaajien nimet "
             "pilkulla erotettuna.\n"
             "(esim. /joukkueet 4, Timppa, Tomppa)\n\n"
             "/osakilpailut komennolla voit tarkastella osakilpailuja, jotka on "
             "lisätty tietokantaan. Tulosteeseen on merkitty onko yksittäinen "
             "kilpailu jo suoritettu, vai vasta tulossa.\n"
             "(esim. /osakilpailut)\n\n"
             "".format(yes))
    apu.botM(update, context,
             "Komennot jotka vaativat luvan {}\n\n"  # ------------
             "/uusi komennolla voit lisätä uusia pelaajia tietokantaan. "
             "Oletuksena uudet pelaajat eivät ole maksaneet liiga-maksua.\n"
             "(esim. /uusi Timppa, Tomppa)\n\n"
             "/maksu komennolla voit päivittää henkilön liiga-maksun tilan.\n"
             "(esim. /maksu Timppa, Tomppa)\n\n"
             "/kroke komennolla voit lisätä osakilpailun tietokantaan. Ajamalla "
             "komennon ilman parametrejä, lisää komento tämän päivän "
             "osakilpaluksi. Jos komennolle antaa parametriksi päivämäärän "
             "muodossa dd.mm, tekee se osakilpilun kyseiselle päivälle.\n"
             "(esim. /kroke)\n"
             "(esim. /kroke 6.9)\n\n"
             "/sijoitus komennolla voit lisätä pelaajille sijotuksen "
             "osakilpailussa. Jotta sijoituksen voi lisätä, on kyseinen päivä "
             "oltava lisätty aiemmin /kroke komennolla. Lisäksi pelaajien on "
             "löydyttävä tietokannasta.\n"
             "(esim. /sijoitus 2, Timppa, Tomppa)\n\n"
             "/poista komennolla voit poistaa yksittäisen henkilön "
             "tietokannasta. Tällöin häviää tiedot henkilön liigamaksun tilasta "
             "ja jokainen osakilpailun sija.\n"
             "(esim. /poista Timppa)\n\n"
             "/nimi komennolla voit vaihtaa tietokannassa olevan pelaajan nimen. "
             "Anna ensimmäiseksi parametriksi vanha nimi ja toiseksi parametriksi "
             "uusi nimi.\n"
             "(esim. /nimi Timppa, Tomppa)\n\n"
             "/piste komennolla voit lisätä tai muuttaa yksittäisen pelaajan "
             "tietoja eri osakilpailuista. Jos pelaajalla ei ole vielä "
             "merkintää halutun päivän osakilpailussa, lisätään uusi tulos. "
             "Muussa tapauksessa vanhaa tulosta muutetaan. Ensimmäinen parametri "
             "on päivämäärä muodossa dd.mm, toinen parametri on pelaajan nimi ja "
             "kolmas parametri on sijoitus.\n"
             "(esim. /piste 6.9, Timppa, 1)\n\n"
             "".format(no))


# -----------------------------------UUSI---------------------------------------
def uusi(update, context):
    user = update.effective_user.id
    if not apu.permit(user):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Sinulla ei ole oikeuksia lisätä uusia "
                                      "henkilöitä tietokantaan")
        return
    names = apu.names(context.args)
    if names[0] == '':
        apu.botM(update, context,
                 "Anna parametriksi pelaajan nimi, jonka haluat lisätä "
                 "tietokantaan. Jos haluat lisätä useamman pelaajan kerralla, "
                 "erota nimet pilkulla.")
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


# -----------------------------------MAKSU--------------------------------------
def maksu(update, context):
    user = update.effective_user.id
    if not apu.permit(user):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Sinulla ei ole oikeuksia muuttaa "
                                 "pelaajien liigamaksun tilaa.")
        return
    names = apu.names(context.args)
    if names[0] == '':
        apu.botM(update, context,
                 "Anna argumentiksi vähintään yksi henkilö, jonka haluat "
                 "merkitä maksaneeksi.")
        return
    conn = sqlite3.connect(apu.db_path)
    cursor = conn.cursor()
    sel = """
        SELECT *
        FROM Maksut
        WHERE nimi = ?
    """
    added = []
    notadded = []
    for name in names:
        cursor.execute(sel, (name,))
        rows = cursor.fetchall()
        if len(rows) == 0:
            notadded.append(name)
        else:
            added.append(name)
    upd = """
        UPDATE Maksut
        SET maksu = 1
        WHERE nimi = ?
    """
    for name in added:
        cursor.execute(upd, (name,))
    conn.commit()
    conn.close()
    if len(notadded) == 0:
        apu.botM(update, context,
                 "Maksu päivitetty onnistuneesti pelaajille.")
    elif len(added) == 0:
        apu.botM(update, context,
                 "Ketään kyseisistä pelaajista ei ole vielä lisätty "
                 "tietokantaan. Lisää pelaajat ensin komennolla /uusi.")
    else:
        apu.botM(update, context, "Maksu päivitetty pelaajille {}. Pelaajia"
                 " {} ei ole vielä lisätty tietokantaan. "
                 "Lisää pelaajat ensin komennolla /uusi."
                 "".format(added, notadded))


# -----------------------------------KROKE--------------------------------------
def kroke(update, context):
    user = update.effective_user.id
    if not apu.permit(user):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Sinulla ei ole oikeuksia lisätä uusia "
                                      "osakilpailuita.")
        return
    names = apu.names(context.args)
    if names[0] == '':
        date = update.message.date
        pv = date.day
        kuu = date.month
        conn = sqlite3.connect(apu.db_path)
        cursor = conn.cursor()
        sel = """
            SELECT *
            FROM Kroket
            WHERE pv = ? AND kuu = ?
        """
        ins = """
            INSERT INTO Kroket
            VALUES(?, ?)
        """
        cursor.execute(sel, (pv, kuu))
        rows = cursor.fetchall()
        if len(rows) == 0:
            cursor.execute(ins, (pv, kuu))
            apu.botM(update, context,
                     "Osakilpailu lisätty tietokantaan.")
            conn.commit()
        else:
            apu.botM(update, context,
                     "Osakilpailu on jo tietokannassa.")
        conn.close()
    elif len(names) == 1:
        pvm = names[0].split(".")
        if not len(pvm) == 2:
            apu.botM(update, context,
                     "Anna parametriksi päivämäärä, jolle haluat "
                     "lisätä osakilpailun, muodossa dd.mm")
            return
        if not pvm[0].isdigit() or not pvm[1].isdigit():
            apu.botM(update, context,
                     "Anna parametriksi päivämäärä dd.mm, jolle haluat lisätä "
                     "osakilpailun.")
            return
        pv = int(pvm[0])
        kuu = int(pvm[1])
        conn = sqlite3.connect(apu.db_path)
        cursor = conn.cursor()
        sel = """
            SELECT *
            FROM Kroket
            WHERE pv = ? AND kuu = ?
        """
        ins = """
            INSERT INTO Kroket
            VALUES(?, ?)
        """
        cursor.execute(sel, (pv, kuu))
        rows = cursor.fetchall()
        if len(rows) == 0:
            cursor.execute(ins, (pv, kuu))
            apu.botM(update, context,
                     "Osakilpailu lisätty tietokantaan.")
            conn.commit()
        else:
            apu.botM(update, context,
                     "Osakilpailu on jo tietokannassa.")
        conn.close()


# -----------------------------------SIJOITUS-----------------------------------
def sijoitus(update, context):
    user = update.effective_user.id
    if not apu.permit(user):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Sinulla ei ole oikeuksia lisätä uusia "
                                 "sijoituksia tietokantaan")
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
    sel1 = """
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
        cursor.execute(sel1, (name, date.day, date.month))
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


# -----------------------------------TULOKSET-----------------------------------
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
            SELECT nimi, maksu, min(pisteet) AS pisteet
            FROM (
                SELECT nimi, maksu, pist as pisteet
                FROM (SELECT nimi, maksu, sum(pisteet) as pist
                      FROM Maksut, Tapahtumat
                      WHERE nimi = ukko
                      GROUP BY nimi
                      ORDER BY -SUM(pisteet)
                      LIMIT 10
                      )
                    Union
                select distinct a.ukko, maksu, pisteet
                FROM(
                    SELECT t1.ukko, max(t1.pisteet+ t2.pisteet + t3.pisteet) as pisteet
                    FROM Tapahtumat AS t1, Tapahtumat AS t2, Tapahtumat AS t3
                    WHERE t1.ukko = t2.ukko
                        AND t3.ukko = t2.ukko
                        AND t1.kuu * 100 + t1.pv != t2.kuu * 100 + t2.pv
                        AND t1.kuu * 100 + t1.pv != t3.kuu * 100 + t3.pv
                        AND t3.kuu * 100 + t3.pv != t2.kuu * 100 + t2.pv
                    GROUP BY t1.ukko
                    ) AS a, Maksut
                WHERE nimi = a.ukko
            )
            GROUP BY nimi
            ORDER BY -min(pisteet)
            LIMIT 10
        """
        cursor.execute(sel)
        rows = cursor.fetchall()
        conn.close()
        no = emojize(":x:", use_aliases=True)
        yes = emojize(":white_check_mark:", use_aliases=True)
        res = """```
Kymmenen parasta pelaajaa:
==========================
Pisteet Maksu Nimi
"""
        for r in rows:
            m = yes
            if r[1] == 0:
                m = no
            p = r[2]
            if p < 10:
                p = str(p) + " "
            res = res + """
{}      {}      {}""".format(p, m, r[0])
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


# -----------------------------------PELAAJAT-----------------------------------
def pelaajat(update, context):
    conn = sqlite3.connect(apu.db_path)
    cursor = conn.cursor()
    sel = """
        SELECT *
        FROM Maksut
        ORDER BY -maksu, nimi
    """
    cursor.execute(sel)
    rows = cursor.fetchall()
    conn.close()
    no = emojize(":x:", use_aliases=True)
    yes = emojize(":white_check_mark:", use_aliases=True)
    res = """```
Pelaajien maksut:
=================
Maksu Nimi
"""
    for r in rows:
        m = yes
        if r[1] == 0:
            m = no
        res = res + """
{}      {}""".format(m, r[0])
    res = res + "```"
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=res,
                             parse_mode=telegram.ParseMode.MARKDOWN)


# -----------------------------------POISTA-------------------------------------
def poista(update, context):
    user = update.effective_user.id
    if not apu.permit(user):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Sinulla ei ole oikeuksia poistaa "
                                 "henkilöitä tietokannasta")
        return
    names = apu.names(context.args)
    if names[0] == '' or len(names) > 1:
        apu.botM(update, context,
                 "Anna argumentiksi yhden pelaajan nimi, jonka haluat poistaa "
                 "tietokannasta. Tämä komento poistaa myös kaikki pelaajan"
                 "sijoitukset osakilpailuista.")
    else:
        conn = sqlite3.connect(apu.db_path)
        cursor = conn.cursor()
        sel1 = """
            SELECT *
            FROM Maksut
            WHERE nimi = ?
        """
        del1 = """
            DELETE
            FROM Maksut
            WHERE nimi = ?
        """
        del2 = """
            DELETE
            FROM Tapahtumat
            WHERE ukko = ?
        """
        cursor.execute(sel1, (names[0],))
        rows = cursor.fetchall()
        if len(rows) == 0:
            apu.botM(update, context,
                     "Kyseinen pelaaja ei ole tietokannassa, joten häntä ei "
                     "voitu poistaa.")
            conn.close()
            return
        cursor.execute(del1, (names[0],))
        cursor.execute(del2, (names[0],))
        conn.commit()
        conn.close()
        apu.botM(update, context,
                 "Pelaaja poistettu tietokannasta.")


# -----------------------------------NIMI---------------------------------------
def nimi(update, context):
    user = update.effective_user.id
    if not apu.permit(user):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Sinulla ei ole oikeuksia "
                                 "muuttaapelaajien nimiä")
        return
    names = apu.names(context.args)
    if names[0] == '' or not len(names) == 2:
        apu.botM(update, context,
                 "Anna 1. argumentiksi yhden pelaajan nimi, jonka haluat "
                 "muuttaa ja 2. argumentiksi uusi nimi.")
        return
    conn = sqlite3.connect(apu.db_path)
    cursor = conn.cursor()
    sel1 = """
        SELECT *
        FROM Maksut
        WHERE nimi = ?
    """
    upd1 = """
        UPDATE Maksut
        SET nimi = ?
        WHERE nimi = ?
    """
    upd2 = """
        UPDATE Tapahtumat
        SET ukko = ?
        WHERE ukko = ?
    """
    cursor.execute(sel1, (names[0],))
    rows = cursor.fetchall()
    if len(rows) == 0:
        apu.botM(update, context,
                 "Kyseinen pelaaja ei ole tietokannassa, joten hänen nimeä ei "
                 "voitu muuttaa.")
        conn.close()
        return
    cursor.execute(sel1, (names[1],))
    rows = cursor.fetchall()
    if not len(rows) == 0:
        apu.botM(update, context,
                 "Tietokannassa on jo henkilö, jonka nimi on sama kuin "
                 "parametriksi annettu uusi nimi. Nimeä ei muutettu.")
        conn.close()
        return
    cursor.execute(upd1, (names[1], names[0]))
    cursor.execute(upd2, (names[1], names[0]))
    conn.commit()
    conn.close()
    apu.botM(update, context,
             "Pelaajan nimi muutettu.")


# -----------------------------------PISTE--------------------------------------
def piste(update, context):
    user = update.effective_user.id
    if not apu.permit(user):
        context.bot.send_message(chat_id=update.effective_chat.id,
                                 text="Sinulla ei ole oikeuksia poistaa "
                                 "henkilöitä tietokannasta")
        return
    names = apu.names(context.args)
    if names[0] == '' or not len(names) == 3:
        apu.botM(update, context,
                 "Anna ensimmäiseksi parametriksi päivämäärä, jolle haluat "
                 "lisätä tai muuttaa pisteet ja toiseksi paramatriksi henkilön, "
                 "jolle tämä muutos tehdään. Anna kolmanneksi parametriksi "
                 "uusi sijoitus.")
        return
    pvm = names[0].split(".")
    if not len(pvm) == 2:
        apu.botM(update, context,
                 "Anna ensimmäiseksi parametriksi päivämäärä, jolle haluat "
                 "lisätä tai muuttaa pisteet, muodossa dd.mm")
        return
    if not pvm[0].isdigit() or not pvm[1].isdigit() or not names[2].isdigit():
        apu.botM(update, context,
                 "Anna ensimmäiseksi parametriksi päivämäärä dd.mm, jolle haluat "
                 "lisätä tai muuttaa pisteet. Anna kolmanneksi parametriksi "
                 "uusi sijoitus.")
        return
    if int(names[2]) not in range(1, 10):
        apu.botM(update, context,
                 "Anna sijoitus, joka on välillä [1,9].")
        return
    pv = int(pvm[0])
    kuu = int(pvm[1])
    name = names[1]
    sij = int(names[2])
    p = apu.switch(sij)
    conn = sqlite3.connect(apu.db_path)
    cursor = conn.cursor()
    sel1 = """
        SELECT *
        FROM Tapahtumat
        WHERE ukko = ? AND pv = ? AND kuu = ?
    """
    sel2 = """
        SELECT *
        FROM Kroket
        WHERE pv = ? AND kuu = ?
    """
    upd1 = """
        UPDATE Tapahtumat
        SET pisteet = ?
        WHERE ukko = ? AND pv = ? AND kuu = ?
    """
    ins1 = """
        INSERT INTO Tapahtumat
        VALUES(?, ?, ?, ?)
    """
    cursor.execute(sel1, (name, pv, kuu))
    rows1 = cursor.fetchall()
    cursor.execute(sel2, (pv, kuu))
    rows2 = cursor.fetchall()
    if len(rows1) == 0 and len(rows2) == 1:
        cursor.execute(ins1, (name, pv, kuu, p))
        conn.commit()
        apu.botM(update, context,
                 "Henkilöllä ei ollut vielä merkintää kyseisen päivän "
                 "osakilpailusta, joten se lisättiin.")
    elif len(rows1) > 0 and len(rows2) == 1:
        cursor.execute(upd1, (p, name, pv, kuu))
        conn.commit()
        apu.botM(update, context,
                 "Henkilön sijoitus osakilpilussa muutettu onnistuneesti")
    else:
        apu.botM(update, context,
                 "Kyseiselle päivälle ei ole lisätty osakilpailua. Komennolla "
                 "/kroke dd.mm voit lisätä osakilpailun tietylle päivälle.")
        return
    conn.close()


# -----------------------------------OSAKILPAILUT-------------------------------
def osakilpailut(update, context):
    conn = sqlite3.connect(apu.db_path)
    cursor = conn.cursor()
    sel = """
        SELECT *
        FROM Kroket
        ORDER BY kuu, pv
    """
    cursor.execute(sel)
    rows = cursor.fetchall()
    conn.close()
    date = update.message.date
    pv = date.day
    kuu = date.month
    today = emojize(":100:", use_aliases=True)
    old = emojize(":white_check_mark:", use_aliases=True)
    new = emojize(":clock9:", use_aliases=True)
    res = """```
Osakilpailut:
=============
Tila Pvm
"""
    for r in rows:
        m = old
        if r[0] == pv and r[1] == kuu:
            m = today
        elif r[1] > kuu or (r[1] == kuu and r[0] > pv):
            m = new
        res = res + """
{}      {}.{}""".format(m, r[0], r[1])
    res = res + "```"
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=res,
                             parse_mode=telegram.ParseMode.MARKDOWN)


# -----------------------------------JOUKKUEET----------------------------------
def joukkueet(update, context):
    names = apu.names(context.args)
    if not names[0].isdigit() or len(names) < 2:
        apu.botM(update, context,
                 "Anna ensimmäisenä parametrina joukkueiden määrä ja sen "
                 "jälkeen pelaajien nimet pilkulla erotettuna.")
        return
    num = int(names[0])
    names = names[1:]
    random.shuffle(names)
    list = [None] * num
    for n in range(0, num):
        list[n] = """
{}.""".format(n + 1)
    res = """```
Joukkueet:"""
    c = 0
    for name in names:
        if c < num:
            list[c % num] += "{}".format(name)
        else:
            list[c % num] += ",{}".format(name)
        c += 1
    for s in list:
        res = res + s
    res = res + "```"
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=res,
                             parse_mode=telegram.ParseMode.MARKDOWN)
