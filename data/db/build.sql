CREATE TABLE IF NOT EXISTS exp(
    UserID integer PRIMARY KEY,
    XP integer,
    Level integer
    XPLock test DEFAULT CURRENT_TIMESTAMP
);
