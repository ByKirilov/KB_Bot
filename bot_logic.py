import datetime

import schedule
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials

import config
from bot import bot
from data.UserIds import user_ids

five_minutes = datetime.datetime.strptime('05', '%M')
fifteen_minutes = datetime.datetime.strptime('15', '%M')


def start(message):
    bot.send_message(message.chat.id, 'Привет! Надеюсь, я стану удобным инструментом для вас!')
    user_ids.add_user_id(message.chat.id)


def stop(message):
    bot.send_message(message.chat.id, 'Пока!')
    user_ids.remove_user_id(message.chat.id)


def today_schedule(chat_id=None):
    msg = _get_schedule()
    if not chat_id:
        for chat in user_ids.users_ids:
            bot.send_message(chat, msg, parse_mode='HTML')
    else:
        bot.send_message(chat_id, msg, parse_mode='HTML')


def tomorrow_schedule(chat_id=None):
    msg = _get_schedule(tomorrow=True)
    bot.send_message(chat_id, msg, parse_mode='HTML')


def bot_all(chat_id):
    with open('data/group_members.txt', 'r') as file:
        members = file.readlines()
        while len(members) > 0:
            msg = ''.join(members[-3:])
            members = members[:-3]
            bot.send_message(chat_id, msg)


def bot_help(chat_id):
    msg = 'Я - бот для нужд группы КБ.\n' \
          'Я ежедневно отправляю расписание. ' \
          'Ты можешь начать со мной личную переписку и тогда я буду слать его лично тебе. ' \
          'Также я отправляю напоминания за 5 и за 15 минут до пары, чтобы у тебя была возможность подготовиться.\n' \
          'Ещё во мне реализована функция, которую все так ждут от телеграмма - тег всех участников беседы (работает только для Секты Ананананичева).\n\n' \
          'Мои команды:\n' \
          '/help - вызов данного сообщения\n' \
          '/start - начать присылать автоматические напоминания о парах\n' \
          '/stop - закончить присылать автоматические напоминания о парах\n' \
          '/all, /channel - тег всех участников Секты Анананичева\n' \
          '/today_schedule - расписание на сегодня\n' \
          '/tomorrow_schedule - расписание на завтра\n\n' \
          'Я ещё буду дорабатываться. Если есть идеи фич, пиши @ars36927.'
    bot.send_message(chat_id, msg)


def _get_schedule(tomorrow=False):
    events = _get_events(tomorrow)
    if not events:
        return f'Нет пар и событий на {"завтра" if tomorrow else "сегодня"}'
    else:
        msg = f'<b>События на {"завтра" if tomorrow else "сегодня"}:</b>\n\n'
        events = map(lambda ev: _make_event_message(ev), events)
        return msg + '\n\n'.join(events)


def _get_events(tomorrow=False):
    time_min = datetime.datetime.today()
    if tomorrow:
        time_min += datetime.timedelta(days=1)
    time_max = time_min + datetime.timedelta(days=1)
    time_min = time_min.date().isoformat() + 'T00:00:01.0Z'  # 'Z' indicates UTC time
    time_max = time_max.date().isoformat() + 'T00:00:01.0Z'  # 'Z' indicates UTC time

    credentials = ServiceAccountCredentials.from_json_keyfile_name(config.client_secret_calendar,
                                                                   'https://www.googleapis.com/auth/calendar.readonly')
    service = build('calendar', 'v3', credentials=credentials)
    eventsResult = service.events().list(
        calendarId=config.calendar_id,
        timeMin=time_min,
        timeMax=time_max,
        maxResults=100,
        singleEvents=True,
        orderBy='startTime') \
        .execute()
    return eventsResult.get('items', [])


def _make_event_message(event):
    if 'description' not in event.keys():
        ev_desc = 'Нет описания'
    else:
        ev_desc = event['description']

    ev_title = event['summary']
    cal_link = f'<a href="{event["htmlLink"]}">Подробнее...</a>'
    ev_start = event['start'].get('dateTime')
    dt_obj = datetime.datetime.strptime(ev_start, '%Y-%m-%dT%H:%M:%S%z')
    ev_start = dt_obj.strftime('%H:%M')
    return f'{ev_start}\n{ev_title}\n{ev_desc}\n{cal_link}'


def _get_event_start(event):
    ev_start = event['start'].get('dateTime')
    dt_obj = datetime.datetime.strptime(ev_start, '%Y-%m-%dT%H:%M:%S%z')
    return dt_obj.strftime('%H:%M')


def _job_reminder(msg):
    for user in user_ids.users_ids:
        bot.send_message(user, msg, parse_mode='HTML')
    return schedule.CancelJob


def _add_reminder(remind_time, msg):
    schedule.every().day.at(remind_time).do(_job_reminder, msg)


def _format_time_to_schedule(time):
    result = f'{time}'[:-3]
    if len(result) == 4:
        result = '0' + result
    return result


def set_reminders():
    events = _get_events()
    for event in events:
        ev_start = _get_event_start(event)
        ev_msg = _make_event_message(event)

        ev_time = datetime.datetime.strptime(ev_start, '%H:%M')
        remind_time = ev_time - five_minutes
        _add_reminder(_format_time_to_schedule(remind_time), 'Через 5 минут начнется:\n' + ev_msg[5:])
        remind_time = ev_time - fifteen_minutes
        _add_reminder(_format_time_to_schedule(remind_time), 'Через 15 минут начнется:\n' + ev_msg[5:])
