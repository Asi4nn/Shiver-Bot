CREATE TABLE IF NOT EXISTS birthdays (
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
    message text
);