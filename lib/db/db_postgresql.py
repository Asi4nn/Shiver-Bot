import psycopg2
from os import environ
from datetime import datetime
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import create_engine

try:
    DATABASE_URL = environ['DATABASE_URL']
    split = DATABASE_URL.split("//")
    DATABASE_URL = "postgresql+psycopg2://" + split[1]
except KeyError:
    DATABASE_URL = "postgresql+psycopg2://postgres:Leowang14@127.0.0.1:5432/postgres"

engine = create_engine(DATABASE_URL, echo=False)

conn = None


def connect():
    global conn
    conn = engine.connect().execution_options(autocommit=True)

    # create the db for the first time
    conn.execute('''CREATE TABLE IF NOT EXISTS birthdays (
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

    # conn.commit()
    time = datetime.now().strftime("[%H:%M:%S]")
    print(time, "Connected to Database")


def commit():
    time = datetime.now().strftime("[%H:%M:%S]")
    print(time, "Saving to Database")
    # conn.commit()


def autosave(sch):
    sch.add_job(commit, CronTrigger(second=0))


def close():
    time = datetime.now().strftime("[%H:%M:%S]")
    print(time, "Closing connection to database")


def field(command, *values):
    conn.execute(command, tuple(values))

    fetch = conn.fetchone()
    if fetch is not None:
        return fetch[0]


def record(command, *values):
    conn.execute(command, tuple(values))

    return conn.fetchone()


def records(commands, *values):
    conn.execute(commands, tuple(values))

    return conn.fetchall()


def column(command, *values):
    conn.execute(command, *values)

    return [item[0] for item in conn.fetchall()]


def execute(command, *values):
    conn.execute(command, tuple(values))


def multiexec(command, value_set):
    conn.executemany(command, value_set)
