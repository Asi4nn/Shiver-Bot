from os import environ
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.engine.mock import MockConnection

try:
    DATABASE_URL = environ['DATABASE_URL']
    split = DATABASE_URL.split("//")
    DATABASE_URL = "postgresql+psycopg2://" + split[1]
except KeyError:
    DATABASE_URL = "postgresql+psycopg2://postgres:Leowang14@127.0.0.1:5432/postgres"

engine = create_engine(DATABASE_URL, echo=False)

conn: MockConnection = engine.connect().execution_options(autocommit=True)


# build db
def build():
    conn.execute('''CREATE TABLE IF NOT EXISTS birthdays (
                            UserID bigint PRIMARY KEY,
                            GuildID bigint,
                            date text
                        );

                        CREATE TABLE IF NOT EXISTS channels (
                            GuildID bigint PRIMARY KEY,
                            channel bigint,
                            cmdchannel bigint
                        );

                        CREATE TABLE IF NOT EXISTS messages (
                            MessageID bigint PRIMARY KEY,
                            guild text,
                            channel text,
                            author text,
                            time text,
                            message text,
                            status text
                        );''')
    time = datetime.now().strftime("[%H:%M:%S]")
    print(time, "Built database")


def connect():
    global conn

    # modify db
    conn.execute('''CREATE TABLE IF NOT EXISTS birthdays (
                            UserID bigint PRIMARY KEY,
                            GuildID bigint,
                            date text
                        );

                        CREATE TABLE IF NOT EXISTS channels (
                            GuildID bigint PRIMARY KEY,
                            channel bigint,
                            cmdchannel bigint
                        );

                        CREATE TABLE IF NOT EXISTS messages (
                            MessageID bigint PRIMARY KEY,
                            guild text,
                            channel text,
                            author text,
                            time text,
                            message text,
                            status text
                        );''')

    time = datetime.now().strftime("[%H:%M:%S]")
    print(time, "Connected to Database")


def close():
    time = datetime.now().strftime("[%H:%M:%S]")
    print(time, "Closing connection to database")


def field(command, *values):
    res = conn.execute(command, tuple(values))

    fetch = res.fetchone()
    if fetch is not None:
        return fetch[0]


def record(command, *values):
    res = conn.execute(command, values)

    return res.fetchone()


def records(commands, *values):
    res = conn.execute(commands, values)

    return res.fetchall()


def column(command, *values):
    res = conn.execute(command, *values)

    return [item[0] for item in res.fetchall()]


def execute(command, *values):
    conn.execute(command, tuple(values))


def multiexec(command, value_set):
    conn.executemany(command, value_set)
