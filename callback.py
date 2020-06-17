import sqlite3
import apu
import telegram
from emoji import emojize
import random
from datetime import datetime
from logg import Logger

logger = Logger(apu.log_path).logger


# -----------------------------------START--------------------------------------
def start(update, context):
    user = update.effective_user.id
    if apu.permit(user):
        logger.info(update.effective_user.full_name + " started the bot and "
                    "has editing permission.")
    else:
        logger.info(update.effective_user.full_name + " started the bot.")
    apu.botM(update, context,
             "Olen botti, joka ylläpitää konklaavin kesäliigan tietokantaa. "
             "/help komennolla saat listauksen käytössä olevista komennoista.")


# -----------------------------------HELP---------------------------------------
def help(update, context):
    no = emojize(":skull_and_crossbones:", use_aliases=True)
    yes = emojize(":yum:", use_aliases=True)
    user = update.effective_user.id
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
    if not apu.permit(user):
        return
    apu.botM(update, context,
             "Komennot jotka vaativat luvan {}\n\n"  # ------------
             "/uusi komennolla voit lisätä uusia pelaajia tietokantaan. "
             "Oletuksena uudet pelaajat eivät ole maksaneet liiga-maksua.\n"
             "(esim. /uusi Timppa, Tomppa)\n\n"
             "/maksu komennolla voit päivittää henkilön liiga-maksun tilan.\n"
             "(esim. /maksu Timppa, Tomppa)\n\n"
             "/pisteet komennolla voit lisätä pelaajille pisteet "
             "osakilpailussa. Jotta pisteet voi lisätä, on kyseinen päivä "
             "oltava lisätty aiemmin /kroke komennolla. Lisäksi pelaajien on "
             "löydyttävä tietokannasta.\n"
             "(esim. /pisteet 2, Timppa, Tomppa)\n\n"
             "/piste komennolla voit lisätä tai muuttaa yksittäisen pelaajan "
             "tietoja eri osakilpailuista. Jos pelaajalla ei ole vielä "
             "merkintää halutun päivän osakilpailussa, lisätään uusi tulos. "
             "Muussa tapauksessa vanhaa tulosta muutetaan. Ensimmäinen parametri "
             "on päivämäärä muodossa dd.mm, toinen parametri on pelaajan nimi ja "
             "kolmas parametri on pisteet.\n"
             "(esim. /piste 6.9, Timppa, 5)\n\n"
             "/poista komennolla voit poistaa yksittäisen henkilön "
             "tietokannasta. Tällöin häviää tiedot henkilön liigamaksun tilasta "
             "ja jokainen osakilpailun sija.\n"
             "(esim. /poista Timppa)\n\n"
             "/nimi komennolla voit vaihtaa tietokannassa olevan pelaajan nimen. "
             "Anna ensimmäiseksi parametriksi vanha nimi ja toiseksi parametriksi "
             "uusi nimi.\n"
             "(esim. /nimi Timppa, Tomppa)\n\n"
             "".format(no))
    if not user == 648172340:
        return
    apu.botM(update, context,
             "/kroke komennolla voi lisätä uuden osakilpailun.\n"
             "(esim. /kroke 6.9)\n\n"
             "/delete komennolla voit poistaa osakilpailun.\n"
             "(esim. /delete 6.9)\n\n"
             )


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
                    UNION
                SELECT DISTINCT a.ukko, maksu, pisteet
                FROM(
                    SELECT t1.ukko, max(t1.pisteet+ t2.pisteet + t3.pisteet) as pisteet
                    FROM Tapahtumat AS t1, Tapahtumat AS t2, Tapahtumat AS t3
                    WHERE t1.ukko = t2.ukko
                        AND t3.ukko = t2.ukko
                        AND t1.pvm != t2.pvm
                        AND t1.pvm != t3.pvm
                        AND t3.pvm != t2.pvm
                    GROUP BY t1.ukko
                    ) AS a, Maksut
                WHERE nimi = a.ukko
            )
            GROUP BY nimi
            ORDER BY -min(pisteet), -maksu, nimi
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
 Pisteet Tila Nimi
"""
        for r in rows:
            m = yes
            if r[1] == 0:
                m = no
            p = r[2]
            if p < 10:
                p = str(p) + " "
            res = res + """
    {}    {}  {}""".format(p, m, r[0])
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
        cursor.execute(sel1, (names[0].lower(),))
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
            ORDER BY pvm
        """
        cursor.execute(sel, (names[0].lower(),))
        rows = cursor.fetchall()
        conn.close()
        res = """```
Pelaajan sijoittumiset:
=======================
     Pvm  Pisteet
"""
        for r in rows:
            s = r[1]
            sta = s[2:]
            end = s[:2]
            pre = ''
            flag = 0
            if s[0] == '0':
                end = end[1:]
                pre = ' '
                flag = 1
            if s[2] == '0':
                sta = sta[1]
                if flag == 1:
                    end = end + ' '
                else:
                    pre = ' '
            sta = pre + sta
            pvm = '.'.join([sta, end])
            res = res + """
    {}    {}""".format(pvm, r[2])
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
   {}   {}""".format(m, r[0])
    res = res + "```"
    context.bot.send_message(chat_id=update.effective_chat.id,
                             text=res,
                             parse_mode=telegram.ParseMode.MARKDOWN)


# -----------------------------------OSAKILPAILUT-------------------------------
def osakilpailut(update, context):
    conn = sqlite3.connect(apu.db_path)
    cursor = conn.cursor()
    sel = """
        SELECT *
        FROM Kroket
        ORDER BY pvm
    """
    cursor.execute(sel)
    rows = cursor.fetchall()
    conn.close()
    now = datetime.now()
    pvm = now.strftime("%m%d")
    today = emojize(":100:", use_aliases=True)
    old = emojize(":white_check_mark:", use_aliases=True)
    new = emojize(":clock9:", use_aliases=True)
    res = """```
     Osakilpailut:
========================
Tila Pvm   Nimi
"""
    for r in rows:
        m = old
        s = r[0]
        if s == pvm:
            m = today
        elif s > pvm:
            m = new
        res = res + """
 {}  {} {}""".format(m, ".".join([s[2:4], s[0:2]]), r[1])
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
