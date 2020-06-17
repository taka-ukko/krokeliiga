from telegram.ext import (Updater, CommandHandler)
import apu
from callback import (start, help, tulokset, pelaajat, joukkueet, osakilpailut)
from callback_admin import (uusi, maksu, pisteet, poista, nimi, piste)
from callback_super_admin import (kroke, error, delete)
from os import getenv
import time

token = getenv("KROKE_BOT")


def main():
    print("Waiting for internet connection")
    while not apu.check_internet():
        time.sleep(5)

    apu.tables()

    updater = Updater(token, use_context=True)
    dispatcher = updater.dispatcher
    bot = dispatcher.bot
    bot.send_message(chat_id=-485426871, text="Käynnistyin :D")
    # handlers
    start_handler = CommandHandler('start', start)
    help_handler = CommandHandler("help", help)
    uusi_handler = CommandHandler('uusi', uusi)
    maksu_handler = CommandHandler('maksu', maksu)
    kroke_handler = CommandHandler('kroke', kroke)
    sij_handler = CommandHandler("pisteet", pisteet)
    tul_handler = CommandHandler("tulokset", tulokset)
    pel_handler = CommandHandler("pelaajat", pelaajat)
    poista_handler = CommandHandler("poista", poista)
    joukk_handler = CommandHandler("joukkueet", joukkueet)
    nimi_handler = CommandHandler("nimi", nimi)
    piste_handler = CommandHandler("piste", piste)
    osa_handler = CommandHandler("osakilpailut", osakilpailut)
    del_handler = CommandHandler("delete", delete)
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
    dispatcher.add_handler(del_handler)
    dispatcher.add_error_handler(error)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
