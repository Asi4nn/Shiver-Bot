from re import fullmatch


def is_mention(mention: str):
    return fullmatch("<@!\d{18}>", mention) is not None
