from googletrans import Translator
from langdetect import detect


def translate_to_english(text, src_lang=None):
    """Translates a given text to English."""
    # if not text or not isinstance(text, str):
    #     return ""
    # translator = Translator()
    # if src_lang and src_lang != "en":
    #     try:
    #         return translator.translate(text, src=src_lang, dest="en").text
    #     except Exception as e:
    #         raise PermissionError(e)
    # return text
    return ""

def get_localized_text(data, key, lang_order=["en", "de", "ru", "uk", "pl", "hy"]):
    """
    Gets localized text from a dictionary based on a prioritized list of languages.
    If the text is not in English, it translates it to English.
    """
    for lang in lang_order:
        if lang in data and data[lang]:
            text = data[lang]

            if lang != 'en':
                return translate_to_english(text, src_lang=lang)

            # Check first 5 words for language detection
            sample_text = ' '.join(text.split()[:5])
            try:
                detected_lang = detect(sample_text)
                if detected_lang != 'en':
                    return translate_to_english(text)
                return text
            except:
                # Fallback to original logic if detection fails
                return translate_to_english(text, src_lang=lang)
    return ""
