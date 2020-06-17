import sqlite3
import apu
from logg import Logger

logger = Logger(apu.log_path).logger


# -----------------------------------KROKE--------------------------------------
def kroke(update, context):
    user = update.effective_user.id
    if not user == 648172340:
        apu.botM(update, context,
                 "Sinulla ei ole oikeuksia lisätä uusia osakilpailuita.")
        return
    names = apu.names(context.args)
    sel = """
        SELECT *
        FROM Kroket
        WHERE pvm = ?
    """
    ins = """
        INSERT INTO Kroket
        VALUES(?, ?)
    """
    if names[0] == '':
        apu.botM(update, context,
                 "Anna parametriksi osakilpailun päivämäärä ja osakilpailun "
                 "nimi pilkulla erotettuna.")
        return
    if '' in names:
        apu.botM(update, context,
                 "Anna toisena parametrinä osakilpailun nimi pilkulla "
                 "erotettuna päivämäärästä.")
        return
    if len(names) == 2:
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
        pv = pvm[0]
        kuu = pvm[1]
        name = names[1]
        pvm = apu.fdate(kuu, pv)
        conn = sqlite3.connect(apu.db_path)
        cursor = conn.cursor()
        cursor.execute(sel, (pvm, ))
        rows = cursor.fetchall()
        if len(rows) == 0:
            cursor.execute(ins, (pvm, name))
            apu.botM(update, context,
                     "Osakilpailu lisätty tietokantaan.")
            conn.commit()
            logger.info(update.effective_user.full_name + " added a new playday.")
        else:
            apu.botM(update, context,
                     "Osakilpailu on jo tietokannassa.")
        conn.close()
    else:
        apu.botM(update, context,
                 "Anna parametriksi osakilpailun päivämäärä ja osakilpailun "
                 "nimi pilkulla erotettuna.")


# -----------------------------------DELETE-------------------------------------
def delete(update, context):
    user = update.effective_user.id
    if not user == 648172340:
        apu.botM(update, context,
                 "Sinulla ei ole oikeuksia poistaa osakilpailuita.")
        return
    names = apu.names(context.args)
    if names[0] == '':
        apu.botM(update, context,
                 "Anna parametriksi osakilpailun päivämäärä.")
        return
    if len(names) == 1:
        pvm = names[0].split(".")
        if not len(pvm) == 2:
            apu.botM(update, context,
                     "Anna parametriksi päivämäärä dd.mm, jolta haluat poistaa "
                     "osakilpailun,")
            return
        if not pvm[0].isdigit() or not pvm[1].isdigit():
            apu.botM(update, context,
                     "Anna parametriksi päivämäärä dd.mm, jolta haluat poistaa "
                     "osakilpailun,")
            return
        conn = sqlite3.connect(apu.db_path)
        cursor = conn.cursor()
        pv = pvm[0]
        kuu = pvm[1]
        pvm = apu.fdate(kuu, pv)
        sel1 = """
            SELECT *
            FROM Kroket
            WHERE pvm = ?
        """
        del1 = """
            DELETE
            FROM Kroket
            WHERE pvm = ?
        """
        cursor.execute(sel1, (pvm,))
        rows = cursor.fetchall()
        if len(rows) == 0:
            apu.botM(update, context,
                     "Osakilpailu ei ole tietokannassa.")
            conn.close()
            return
        cursor.execute(del1, (pvm,))
        conn.commit()
        conn.close()
        logger.info(update.effective_user.full_name + " deleted a competition.")
        apu.botM(update, context,
                 "Osakilpailu poistettu tietokannasta.")
    else:
        apu.botM(update, context,
                 "Anna parametriksi päivämäärä, jolta haluat "
                 "poistaa osakilpailun, muodossa dd.mm")


# -----------------------------------ERROR--------------------------------------
def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)
