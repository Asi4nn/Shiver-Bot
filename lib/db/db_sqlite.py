from os.path import isfile, dirname, abspath, join
from os import chdir
from sqlite3 import connect
from datetime import datetime
from apscheduler.triggers.cron import CronTrigger

BASE_DIR = join(dirname(abspath(__file__)), "../../data/db/")
BUILD_PATH = join(BASE_DIR, "build.sql")
DB_PATH = join(BASE_DIR, "database.db")
print(BASE_DIR)
if not isfile(DB_PATH):
    raise FileNotFoundError("database.db not found")
if not isfile(BUILD_PATH):
    raise FileNotFoundError("build.sql not found")

cxn = connect(DB_PATH, check_same_thread=False)
conn = cxn.cursor()


def with_commit(func):
    def inner(*args, **kwargs):
        func(*args, **kwargs)
        commit()

    return inner


@with_commit
def build():
    if isfile(BUILD_PATH):
        scriptexec(BUILD_PATH)


def commit():
    time = datetime.now().strftime("[%H:%M:%S]")
    print(time, "Saving to Database")
    cxn.commit()


def autosave(sch):
    sch.add_job(commit, CronTrigger(second=0))


def close():
    cxn.close()


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


def scriptexec(path):
    with open(path, 'r', encoding='utf-8') as script:
        conn.executescript(script.read())
