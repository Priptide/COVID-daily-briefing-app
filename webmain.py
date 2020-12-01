'''
The webserver running the project
'''

import json
import time
import sched
import sys
import logging
from datetime import datetime, timedelta
from typing import List
import pyttsx3
from flask import Flask
from flask import request
from flask import render_template
from covid_19_stat import get_covid_19_cases
from weather_update import get_weather
from news_filter import get_news

# Create a scheduler and run the flask application also define a log file
S = sched.scheduler(time.time, time.sleep)
APP = Flask(__name__)
logging.basicConfig(filename='sys.log', level=logging.DEBUG)

# Initial module scope definitions
NOTIFICATIONS = []
ALARMS = []
BRIEFING_TIMES = []
NEWS_PROVIDER_PREFERENCES = ()
NEWS_KEY = ""
WEATHER_KEY = ""
CURRENT_CITY = ""
CURRENT_COUNTRY = ""
COVID_BRIEF = ""
KEYS_DICT = ""
NAME = ""
LOGGED_ERRORS = []


def write_to_log(log_text: str, log_info: bool = True) -> None:
    '''
    Used to write any updates or changes too the log file
    '''

    if(log_info):
        logging.info(log_text)
    else:
        logging.error(log_text)


def write_config() -> None:
    '''
    This is for updating the ALARMS and the NOTIFICATIONS to the config log
    '''

    # Update the dictionary with the current ALARMS and NOTIFICATIONS
    KEYS_DICT['Notifications'] = NOTIFICATIONS
    KEYS_DICT['Alarms'] = ALARMS

    # Open and update the config.json file
    with open('config.json', 'w') as config:
        json.dump(KEYS_DICT, config)

    # Log the update
    write_to_log("UPDATED - config file")


def import_config() -> None:
    '''
    Load the config file in and get the API keys aswell as the settings for the
    User
    '''

    # Here we instantiate all the global variables so we can edit them
    global NOTIFICATIONS
    global ALARMS
    global BRIEFING_TIMES
    global NEWS_PROVIDER_PREFERENCES
    global NEWS_KEY
    global WEATHER_KEY
    global CURRENT_CITY
    global CURRENT_COUNTRY
    global COVID_BRIEF
    global KEYS_DICT
    global NAME

    # Load the config.json file
    with open('config.json', 'r') as config:

        # Make sure all the data is loaded correctly, if not
        # we log and error and quit the application
        try:
            # Here we load all saved variables and settings from config.json
            KEYS_DICT = json.load(config)
        except json.decoder.JSONDecodeError:
            # Failed to load, log the error
            write_to_log(
                "Config.json couldn't load - Check the format of the file and retry", False)
            sys.exit()

        # Load api keys
        NEWS_KEY = KEYS_DICT['News_API_Key']
        WEATHER_KEY = KEYS_DICT['Weather_API_Key']

        # Log the loaded keys
        write_to_log("LOADED - API Keys")

        # Load user settings
        CURRENT_CITY = KEYS_DICT['Current_City']
        CURRENT_COUNTRY = KEYS_DICT['Current_Country']
        COVID_BRIEF = KEYS_DICT['Covid_Briefing']
        NAME = KEYS_DICT['Name']
        BRIEFING_TIMES = KEYS_DICT['Briefing_Times']
        NEWS_PROVIDER_PREFERENCES = tuple(
            KEYS_DICT['News_Provider_Preferences'])

        write_to_log("LOADED - User Settings")

        # Load saved data
        NOTIFICATIONS = KEYS_DICT['Notifications']
        ALARMS = KEYS_DICT['Alarms']

        write_to_log("LOADED - Saved NOTIFICATIONS and Alarms")


def load_alarms() -> None:
    '''
    Load the saved ALARMS from the config file, checking that
    they are still in the future and removing those that aren't
    '''

    # Loop through all the ALARMS loaded
    for alarm in ALARMS:

        # Turn their hidden_date into a date time
        alarm_date = datetime.strptime(
            alarm['hidden_date'], '%Y-%m-%d %H:%M:%S')

        # If their alarm_date is in the past then remove
        # it and write that remove to the config file
        if alarm_date <= datetime.now():
            write_to_log("REMOVED - Old alarm at " +
                         str(alarm['hidden_date']) + " was removed")
            ALARMS.remove(alarm)
            write_config()
        elif alarm_date > datetime.now():

            # If the alarm is in the future then
            # work out the time till the alarm
            time_to_alarm = (alarm_date - datetime.now()).total_seconds()

            write_to_log("ADDED - Alarm at " +
                         str(alarm['hidden_date']) + " was added")

            # Add the alarm too the sched too set off run alarm when complete
            S.enter(time_to_alarm, 1, run_alarm,
                    (str(alarm['title']), alarm['has_news'], alarm['has_weather']),)


def check_alarms() -> None:
    '''
    Runs to check all the ALARMS are still valid and
    deletes those that aren't simply an error checker
    '''

    # Enable this comment if you want the alarm check to show in the log
    # write_to_log("Alarms Checked")

    # Loop all ALARMS
    for alarm in ALARMS:

        # Turn their hidden_date into a date time
        alarm_date = datetime.strptime(
            alarm['hidden_date'], '%Y-%m-%d %H:%M:%S')

        # If their alarm_date is in the past then remove
        # it and write that remove to the config file
        if alarm_date <= datetime.now():
            write_to_log("REMOVED - Old alarm at " +
                         str(alarm['hidden_date']) + " was removed")
            ALARMS.remove(alarm)
            write_config()

    # Refresh the index file
    return index


@APP.route('/')
def redirect() -> None:
    '''
    Just a redirect in case you don't open on the index page
    '''
    return index()


@APP.route('/index')
def index() -> None:
    '''
    The main page of the site, which contains the ALARMS, NOTIFICATIONS
    and the ability to add them
    '''

    # start the scheduler running with blocking set too false
    S.run(blocking=False)

    # These are our listeners for NOTIFICATIONS and ALARMS aswell as
    # their labels and whether or not they have weather and news alerts
    delete_notification = request.args.get('notif')
    alarm_request = request.args.get('alarm')
    alarm_label = request.args.get('two')
    has_weather_str = request.args.get('weather')
    has_news_str = request.args.get('news')
    delete_alarm = request.args.get('alarm_item')

    # If a delete notification is picked up, and the type is a string
    # meaning there is text in the listener then cycle through all
    # the NOTIFICATIONS and delete the one with the matching title
    if delete_notification != "" and isinstance(delete_notification, str):

        # Loop through all NOTIFICATIONS
        for notif in NOTIFICATIONS:
            if notif['title'] == delete_notification:
                # Note that we make sure when creating a notification that
                # all the titles are unique
                NOTIFICATIONS.remove(notif)
                write_config()

    # This is the exact same logic as before just with ALARMS
    if delete_alarm != "" and isinstance(delete_alarm, str):

        for alarm in ALARMS:
            if alarm['title'] == delete_alarm:
                # Again every alarm has a unique title
                ALARMS.remove(alarm)
                write_config()

    # Here we run a request for an alarm to be created
    if alarm_request != "" and isinstance(alarm_request, str):

        # We first check the listeners and set wether there is a news
        # and/or weather breifing acordingly
        has_news = False
        if has_news_str == 'news':
            has_news = True

        has_weather = False
        if has_weather_str == 'weather':
            has_weather = True

        # Then pass all these arguments too the add_alarm function
        add_alarm(alarm_request, alarm_label, has_news, has_weather)

    greeting = ""
    current_hour = datetime.now().hour

    # Changes the web page greeting depending on the time of day
    if current_hour < 12:
        greeting = "Good Morning"
    elif current_hour < 18:
        greeting = "Good Afternoon"
    else:
        greeting = "Good Evening"

    # Run the template render with a custom image for the web page aswell
    # as passing a link for a favicon
    return render_template('index.html', title=(greeting + ', ' + NAME + '!'),
                           notifications=NOTIFICATIONS, alarms=ALARMS,
                           favicon='https://bit.ly/3nxV2d2', image='icon.png')


def load_briefings() -> None:
    '''
    Here we load the brieifings from the config and setup the
    scheduler to handle these breifings daily
    '''
    for time_select in BRIEFING_TIMES:
        # First we convert the text into a date time variable
        date_time = datetime.strptime(time_select, '%H:%M')
        curr = datetime.now()
        # Setting the date to today and time to the selected time
        date_time = datetime(year=curr.year, month=curr.month,
                             day=curr.day, hour=date_time.hour,
                             minute=date_time.minute)

        # Here we check if the datetime is in the past
        if date_time < datetime.now():
            # If so we add a days worth of time too it
            date_time = date_time + timedelta(days=1)

        # Calculate the time in second till the alarm is needed to sound
        # Then add too the scheduler passing the time and date for the breifing
        time_to_alarm = (date_time - datetime.now()).total_seconds()
        S.enter(time_to_alarm, 1, run_briefing, (time_select, date_time))


def run_briefing(time_select: str, date_time) -> None:
    '''
    When a briefing time is reched we get the current news stories
    and weather aswell as covid-19 stories if this enabled by the
    user and display them silently in the NOTIFICATIONS
    '''

    # Load in the news and covid stories from the news api
    try:
        news_update, covid_update = get_news(
            CURRENT_COUNTRY, NEWS_KEY, NEWS_PROVIDER_PREFERENCES)
    except ValueError as e:
        message = get_news(
            CURRENT_COUNTRY, NEWS_KEY, NEWS_PROVIDER_PREFERENCES)
        write_to_log(message)
        LOGGED_ERRORS.append(
            message)
        NOTIFICATIONS.append(
            {"title": ("Error - UID:" + str(len(LOGGED_ERRORS))), "content": message})
        # Save the NOTIFICATIONS and the removed alarm too the config
        write_config()
        return index

    # Loop through all the news stories
    for article in news_update:
        # Add the news story as content along with a custom title
        # (effectively a UID for the notification) to the notification pannel
        title = "News Update - " + \
                str(datetime.now().strftime("%d/%m/%Y %H:%M")) +\
            " - Story " + str(news_update.index(article) + 1)
        NOTIFICATIONS.append({"title": title, "content": article})

    # If the user has enabled Covid-19 updates in their config (On by default)
    if COVID_BRIEF:

        # Make sure to run through even if the api is down or we have wrong information
        try:
            # Load in the daily covid cases for the current/nearest city
            total_cases, cases_today = get_covid_19_cases(CURRENT_CITY)
        except ValueError as e:
            message = get_covid_19_cases(CURRENT_CITY)
            write_to_log(message)
            LOGGED_ERRORS.append(
                message)
            NOTIFICATIONS.append(
                {"title": ("Error - UID:" + str(len(LOGGED_ERRORS))), "content": message})
            # Save the NOTIFICATIONS and the removed alarm too the config
            write_config()
            return index

        # Then create a message to show the covid cases for the day
        # aswell as the total covid cases
        message = "Covid-19 cases today in " + CURRENT_CITY + " " + \
            str(cases_today) + " giving a cumulative total of " + \
            str(total_cases) + " in " + CURRENT_CITY

        # Add this message along with a custom
        # dated title too the NOTIFICATIONS
        NOTIFICATIONS.append({"title": "COVID Statistics Update - " + str(
            datetime.now().strftime("%d/%m/%Y %H:%M")), "content": message})

        # Then loop through the covid-19 news articles
        for covid_article in covid_update:

            # Give the article a title using the date and time as UID
            title = "COVID News Update - " + \
                str(datetime.now().strftime("%d/%m/%Y %H:%M")) +\
                " - Story " + str(covid_update.index(covid_article) + 1)

            NOTIFICATIONS.append(
                {"title": title, "content": covid_article})

    # Run the get_weather to open weather api
    # to get the current weather conditions
    try:
        current_temperature, current_pressure, current_humidiy, \
            weather_description = get_weather(CURRENT_CITY, WEATHER_KEY)
    except ValueError as e:
        message = get_weather(CURRENT_CITY, WEATHER_KEY)
        write_to_log(message)
        LOGGED_ERRORS.append(
            message)

        NOTIFICATIONS.append(
            {"title": ("Error - UID:" + str(len(LOGGED_ERRORS))), "content": message})
        # Save the NOTIFICATIONS and the removed alarm too the config
        write_config()
        return index

    # Add the weather to the NOTIFICATIONS
    NOTIFICATIONS.append(
        {"title": ("Weather Update - " +
                   str(datetime.now().strftime("%d/%m/%Y %H:%M"))),
         "content": ("Temperature (in degrees): " +
                     str(int(current_temperature) - 273) +
                     "\n | Atmospheric pressure (in hPa unit): " +
                     str(current_pressure) +
                     "\n | Humidity (as a percentage): " +
                     str(current_humidiy) +
                     "\n | Current weather: " +
                     str(weather_description))})

    # Add a day too the current briefing time
    date_time = date_time + timedelta(days=1)

    # Calculate the time too the next briefing
    # and then re-add it too the scheduler
    time_to_alarm = (date_time - datetime.now()).total_seconds()
    S.enter(time_to_alarm, 1, run_briefing, (time_select, date_time))

    # Refresh the page
    return index


def tts_request(words_to_say: List[str]) -> None:
    '''
    Uses the pyttsx3 library to perform text to speech takes
    a list of strings and cycles through them saying each one
    '''
    # Load a pyttsx3 engine
    engine = pyttsx3.init()

    for words in words_to_say:
        # Say the word and wait until it is complete before moving to the next
        engine.say(words)
        engine.runAndWait()


def add_alarm(alarm_request: str, alarm_label: str, has_news: bool,
              has_weather: bool) -> None:
    '''
    Add an alarm to the sched with the
    posibility of a news and/or a weather briefing
    '''

    # Make sure the alarm date time isn't passed as an empty variable
    if len(alarm_request) > 0:

        # Turn the text of the request into a date time
        date_proper = datetime.strptime(alarm_request, '%Y-%m-%dT%H:%M')

        # Make sure the alarm is in the future
        if date_proper > datetime.now():

            # Create a title for the alarm as the name
            # with the date an time the alarm will go off
            alarm_label = alarm_label + " - " + \
                date_proper.strftime("%d/%m/%Y %H:%M")

            content = ""
            news = "news"

            # If covid-19 briefing is enabled then change the message for news
            if COVID_BRIEF:
                news = "news and COVID-19"

            # Create the content for the alarm telling the user what
            # type of alarm they set, if no briefing then we leave it empty
            if has_news and has_weather:
                content = "Contains a weather, "+news+" briefing"
            elif has_weather:
                content = "Contains a weather briefing"
            elif has_news:
                content = "Contains a "+news+" briefing"

            alarm_index = 1

            # Cycle through the ALARMS and work out the priority for the alarm
            for alarm in ALARMS:

                if alarm['title'] == alarm_label:
                    # Error alarm with the same name and time
                    # present log and notify the user
                    LOGGED_ERRORS.append(
                        "ERROR - Alarm with the same name and time")

                    write_to_log(
                        "ERROR - Alarm with the same name and time")

                    NOTIFICATIONS.append({"title": ("Error - UID:" +
                                                    str(len(LOGGED_ERRORS))),
                                          "content": "ERROR - Alarm with the \
                                              same name and time"})

                    return index

                # If there is already an alarm at this time then
                # add one to this ALARMS priority
                if alarm['hidden_date'] == str(date_proper):
                    alarm_index += 1

                    # Here we turn off it's news or weather if the the other
                    # alarm has it enabled to stop duplicate messages
                    # and text to speach
                    if alarm['has_news']:
                        has_news = False
                    if alarm['has_weather']:
                        has_weather = False

            # Generate a new alarm object with a few hidden variables
            # for it to be readded from the config file if need
            alarm_new = {'title': alarm_label,
                         'content': content,
                         'has_news': has_news,
                         'has_weather': has_weather,
                         'hidden_date': str(date_proper)}

            # Add the alarm to the list of ALARMS aswell as too the sched
            ALARMS.append(alarm_new)

            time_to_alarm = (date_proper - datetime.now()).total_seconds()

            write_to_log("Added - Alarm at " +
                         str(date_proper) + " was added")

            S.enter(time_to_alarm, alarm_index, run_alarm,
                    (alarm_label, has_news, has_weather),)

            # Save the alarm to the config
            write_config()
        else:

            # Log the error and display too the user

            LOGGED_ERRORS.append("ERROR - Alarm added in the past")

            write_to_log(
                "ERROR - Alarm added in the past")

            NOTIFICATIONS.append({"title": ("Error - UID:" +
                                            str(len(LOGGED_ERRORS))),
                                  "content": "ERROR - Alarm \
                                      added in the past"})
            return index
    else:
        # Add Error to log (No arguments passed)
        write_to_log(
            "ERROR TECH - No arguments passed", False)

        return index
    return index


def run_alarm(alarm_label: str, news: bool = False, weather: bool = False) -> None:
    '''
    When an alarm is run we set off a noise aswell as showing
    any updates we need in news or weather
    '''

    text_to_read = []
    title = ""
    alarm_active = False

    # Find the alarm in the ALARMS list and remove it
    for alarm in ALARMS:
        if alarm['title'] == alarm_label:
            ALARMS.remove(alarm)
            alarm_active = True
            continue

    # If we can't find the alarm then return an error
    if not alarm_active:
        # Return error to log only, error alarm doesn't exist
        write_to_log(
            "ERROR TECH - No alarm found", False)
        return index

    write_to_log(
        "ALARM - Alarm: " + alarm_label + " has rung")
    # Add the alarm too the notifcation pannel
    title = "Alarm - " + alarm_label
    NOTIFICATIONS.append({"title": title, "content": (
        "Alarm " + alarm_label + " has rung")})

    # Add the alarm to the text to speech list
    text_to_read.append(("Alarm " + alarm_label + " has rung!"))

    # If news is enabled show the news and if Covid brief enabled show this too
    if news:
        # Same logic as the earlier brieifing just adds
        # the content too the text too speech
        text_to_read.append("News Update")

        # Make sure to still run if an api error is caught
        try:
            news_update, covid_update = get_news(
                CURRENT_COUNTRY, NEWS_KEY, NEWS_PROVIDER_PREFERENCES)
        except ValueError as e:
            message = news_update, covid_update = get_news(
                CURRENT_COUNTRY, NEWS_KEY, NEWS_PROVIDER_PREFERENCES)
            write_to_log(message)
            text_to_read.append(message)
            # Read out all loaded text so far
            tts_request(text_to_read)
            LOGGED_ERRORS.append(
                message)
            NOTIFICATIONS.append(
                {"title": ("Error - UID:" + str(len(LOGGED_ERRORS))), "content": message})
            # Save the NOTIFICATIONS and the removed alarm too the config
            write_config()
            return index

        for article in news_update:
            title = "News Update - " + \
                str(datetime.now().strftime("%d/%m/%Y %H:%M")) +\
                " - Story " + str(news_update.index(article) + 1)

            NOTIFICATIONS.append({"title": title, "content": article})

            text_to_read.append(article)

        if COVID_BRIEF:
            text_to_read.append("COVID-19 Update")

            # Make sure to run through even if the api is down or we have wrong information
            try:
                total_cases, cases_today = get_covid_19_cases(CURRENT_CITY)
            except ValueError as e:
                message = get_covid_19_cases(CURRENT_CITY)
                write_to_log(message)
                text_to_read.append(message)
                # Read out all loaded text so far
                tts_request(text_to_read)
                LOGGED_ERRORS.append(
                    message)
                NOTIFICATIONS.append(
                    {"title": ("Error - UID:" + str(len(LOGGED_ERRORS))), "content": message})
                # Save the NOTIFICATIONS and the removed alarm too the config
                write_config()
                return index

            message = "Covid-19 cases today in " + CURRENT_CITY + " " + \
                str(cases_today) + " giving a cumulative total of " + \
                str(total_cases) + " in " + CURRENT_CITY
            text_to_read.append(message)

            NOTIFICATIONS.append({"title": "COVID Statistics Update - " + str(
                datetime.now().strftime("%d/%m/%Y %H:%M")), "content": message})

            for covid_article in covid_update:
                title = "COVID News Update - " + \
                    str(datetime.now().strftime("%d/%m/%Y %H:%M")) +\
                    " - Story " + str(covid_update.index(covid_article) + 1)

                NOTIFICATIONS.append(
                    {"title": title, "content": covid_article})

                text_to_read.append(covid_article)

    # If weather brief is on then display the weather too
    if weather:
        # Same logic as the earlier brieifing just adds
        # the content too the text too speech
        text_to_read.append("Weather Update")

        # We make sure that there is a correct api key or city set otherwise we call an error
        try:
            current_temperature, current_pressure, current_humidiy, \
                weather_description = get_weather(CURRENT_CITY, WEATHER_KEY)
        except ValueError as e:
            message = get_weather(CURRENT_CITY, WEATHER_KEY)
            write_to_log(message)
            LOGGED_ERRORS.append(
                message)
            text_to_read.append(message)
            # Read out all loaded text so far
            tts_request(text_to_read)
            NOTIFICATIONS.append(
                {"title": ("Error - UID:" + str(len(LOGGED_ERRORS))), "content": message})
            # Save the NOTIFICATIONS and the removed alarm too the config
            write_config()
            return index

        NOTIFICATIONS.append(
            {"title": ("Weather Update - " +
                       str(datetime.now().strftime("%d/%m/%Y %H:%M"))),
             "content": ("Temperature (in degrees): " +
                         str(int(current_temperature) - 273) +
                         "\n | Atmospheric pressure (in hPa unit): " +
                         str(current_pressure) +
                         "\n | Humidity (as a percentage): " +
                         str(current_humidiy) +
                         "\n | Current weather: " +
                         str(weather_description))})
        text_to_read.append(("Temperature (in degrees) | " +
                             str(int(current_temperature) - 273) +
                             "\n | Atmospheric pressure (in hPa unit) | " +
                             str(current_pressure) +
                             "\n | Humidity (as a percentage) | " +
                             str(current_humidiy) +
                             "\n | Current weather | " +
                             str(weather_description)))

    # Save the NOTIFICATIONS and the removed alarm too the config
    write_config()

    # Read out the alarm aswell as any annoucements we added
    tts_request(text_to_read)

    # Refresh the main page
    return index


if __name__ == '__main__':

    # Load all user preferences, api keys and settings from the config file
    import_config()

    # If there are saved ALARMS then properly load and check them
    if len(ALARMS) > 0:
        load_alarms()

    # Check the ALARMS
    check_alarms()

    # If there are set daily briefings then load these
    if len(BRIEFING_TIMES) > 0:
        load_briefings()

    # Run the flask application
    APP.run()
