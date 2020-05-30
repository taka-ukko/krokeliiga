from telegram.ext import (Updater, CommandHandler)
import logging
import apu
from callback import (start, uusi, maksu, sijoitus, kroke, help, tulokset)

logging.basicConfig(format="""%(asctime)s - %(name)s - %(levelname)s -
                    %(message)s""",
                    level=logging.INFO)


def main():
    apu.tables()
    updater = Updater(token=apu.get_token(), use_context=True)
    dispatcher = updater.dispatcher
    # handlers
    start_handler = CommandHandler('start', start)
    uusi_handler = CommandHandler('uusi', uusi)
    maksu_handler = CommandHandler('maksu', maksu)
    kroke_handler = CommandHandler('kroke', kroke)
    sij_handler = CommandHandler("sijoitus", sijoitus)
    help_handler = CommandHandler("help", help)
    tul_handler = CommandHandler("tulokset", tulokset)
    # handlers to dispatchers
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(uusi_handler)
    dispatcher.add_handler(maksu_handler)
    dispatcher.add_handler(sij_handler)
    dispatcher.add_handler(kroke_handler)
    dispatcher.add_handler(help_handler)
    dispatcher.add_handler(tul_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
