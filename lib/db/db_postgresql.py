import psycopg2
from os import environ
from datetime import datetime
from apscheduler.triggers.cron import CronTrigger

DATABASE_URL = environ['DATABASE_URL']
time = datetime.now().strftime("[%H:%M:%S]")

cxn = None
cur = None


def connect():
    global cxn
    global cur
    cxn = psycopg2.connect(database=DATABASE_URL)
    cur = cxn.cursor()

    # create the db for the first time
    cur.execute('''CREATE TABLE IF NOT EXISTS birthdays (
                        UserID integer PRIMARY KEY,
                        GuildID integer,
                        date text
                    );

                    CREATE TABLE IF NOT EXISTS channels (
                        GuildID integer PRIMARY KEY,
                        channel integer
                    );

                    CREATE TABLE IF NOT EXISTS messages (
                        MessageID integer PRIMARY KEY,
                        guild text,
                        channel text,
                        author text,
                        time text,
                        message text,
                        status text
                    );''')
    cxn.commit()

    time = datetime.now().strftime("[%H:%M:%S]")
    print(time, "Connected to Database")


def commit():
    time = datetime.now().strftime("[%H:%M:%S]")
    print(time, "Saving to Database")
    cxn.commit()


def autosave(sch):
    sch.add_job(commit, CronTrigger(second=0))


def close():
    cxn.close()


def field(command, *values):
    cur.execute(command, tuple(values))

    fetch = cur.fetchone()
    if fetch is not None:
        return fetch[0]


def record(command, *values):
    cur.execute(command, tuple(values))

    return cur.fetchone()


def records(commands, *values):
    cur.execute(commands, tuple(values))

    return cur.fetchall()


def column(command, *values):
    cur.execute(command, *values)

    return [item[0] for item in cur.fetchall()]


def execute(command, *values):
    cur.execute(command, tuple(values))


def multiexec(command, value_set):
    cur.executemany(command, value_set)
