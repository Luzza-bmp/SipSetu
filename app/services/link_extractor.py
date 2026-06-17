import re


def extract_links(text):

    pattern = r"https?://[^\s]+"

    return re.findall(pattern, text)
