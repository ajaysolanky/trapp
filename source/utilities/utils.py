def decode_unicode_escape_sequence(s):
    return bytes(s, "utf-8").decode("unicode_escape")
