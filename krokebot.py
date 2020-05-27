from telegram.ext import (Updater, CommandHandler, ConversationHandler,
                          MessageHandler, Filters)
import logging
import apu
from callback import (eka, toka, kolmas, muu, start, uusi, maksu, sijoitus,
                      peruuta)

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
    sij_handler = ConversationHandler(
        entry_points=[CommandHandler("sijoitus", sijoitus)],
        states={
            apu.SCORES: [MessageHandler(Filters.regex('^(Ensimmäinen)$'), eka),
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
