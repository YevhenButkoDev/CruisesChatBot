from bs4 import BeautifulSoup

def remove_html_tags(text):
    """Removes HTML tags from a given text."""
    if not text or not isinstance(text, str):
        return ""
    text = text.replace("&nbsp;", " ")
    text = text.replace("& nbsp;", " ")
    text = text.replace("& Nbsp;", " ")
    return BeautifulSoup(text, "html.parser").get_text()
