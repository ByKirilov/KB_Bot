import threading
import time

import schedule

from bot import bot
from bot_logic import bot_all, today_schedule, tomorrow_schedule, bot_help, start, set_reminders, stop
from config import admin_chat_id


@bot.message_handler(commands=['start', 'go'])
def start_handler(message):
    start(message)


@bot.message_handler(commands=['stop'])
def start_handler(message):
    stop(message.chat.id)


@bot.message_handler(commands=['help'])
def help_handler(message):
    bot_help(message.chat.id)


@bot.message_handler(commands=['today_schedule'])
def today_schedule_handler(message):
    today_schedule(message.chat.id)


@bot.message_handler(commands=['tomorrow_schedule'])
def tomorrow_schedule_handler(message):
    tomorrow_schedule(message.chat.id)


@bot.message_handler(commands=['all', 'channel'])
def all_handler(message):
    bot_all(message.chat.id)


def _bot_pooling():
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        bot.send_message(admin_chat_id, f'Я упал. Причины:\n{e.with_traceback()}')
        _bot_pooling()


job_tread = threading.Thread(target=_bot_pooling)
job_tread.start()
set_reminders()

schedule.every().day.at("00:01").do(set_reminders)
schedule.every().day.at("08:00").do(today_schedule)
while True:
    schedule.run_pending()
    time.sleep(1)
