CREATE TABLE IF NOT EXISTS birthdays (
    UserID bigint,
    GuildID bigint,
    date text,
    PRIMARY KEY (UserID, GuildID)
);

CREATE TABLE IF NOT EXISTS channels (
    GuildID bigint PRIMARY KEY,
    channel bigint
);

CREATE TABLE IF NOT EXISTS messages
(
    MessageID bigint PRIMARY KEY,
    guild     text,
    channel   text,
    author    text,
    time      text,
    message   text,
    status    text
);