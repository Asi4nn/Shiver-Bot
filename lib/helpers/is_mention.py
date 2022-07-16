from re import fullmatch


def is_mention(mention: str):
    return fullmatch(r"<@[!]?\d{18}>", mention) is not None


def get_mention_id(mention_str: str) -> int:
    """
    Given a valid mention str matched using is_mention()
    :param mention_str:
    :return: Mention id
    """
    return int("".join([char for char in mention_str if char.isdigit()]))
