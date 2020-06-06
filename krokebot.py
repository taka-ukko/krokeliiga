from telegram.ext import (Updater, CommandHandler)
import logging
import apu
from callback import (start, uusi, maksu, sijoitus, kroke, help, tulokset,
                      pelaajat, poista, joukkueet, nimi, piste, osakilpailut)
from os import getenv

token = getenv("KROKE_BOT")

logging.basicConfig(format="""%(asctime)s - %(name)s - %(levelname)s -
                    %(message)s""",
                    level=logging.INFO)


def main():
    apu.tables()
    updater = Updater(token, use_context=True)
    dispatcher = updater.dispatcher
    # handlers
    start_handler = CommandHandler('start', start)
    help_handler = CommandHandler("help", help)
    uusi_handler = CommandHandler('uusi', uusi)
    maksu_handler = CommandHandler('maksu', maksu)
    kroke_handler = CommandHandler('kroke', kroke)
    sij_handler = CommandHandler("sijoitus", sijoitus)
    tul_handler = CommandHandler("tulokset", tulokset)
    pel_handler = CommandHandler("pelaajat", pelaajat)
    poista_handler = CommandHandler("poista", poista)
    joukk_handler = CommandHandler("joukkueet", joukkueet)
    nimi_handler = CommandHandler("nimi", nimi)
    piste_handler = CommandHandler("piste", piste)
    osa_handler = CommandHandler("osakilpailut", osakilpailut)
    # handlers to dispatchers
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(uusi_handler)
    dispatcher.add_handler(maksu_handler)
    dispatcher.add_handler(sij_handler)
    dispatcher.add_handler(kroke_handler)
    dispatcher.add_handler(tul_handler)
    dispatcher.add_handler(pel_handler)
    dispatcher.add_handler(poista_handler)
    dispatcher.add_handler(joukk_handler)
    dispatcher.add_handler(nimi_handler)
    dispatcher.add_handler(piste_handler)
    dispatcher.add_handler(osa_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
