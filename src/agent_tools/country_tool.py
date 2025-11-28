import requests
import logging
import os

logger = logging.getLogger(__name__)

# Comprehensive country name mappings: English -> Russian alternatives
COUNTRY_MAPPINGS = {
    # Major countries with common alternative names
    'united arab emirates': ['ОАЭ'],
    'uae': ['ОАЭ'],
    'emirates': ['ОАЭ'],
    'usa': ['США'],
    'united states': ['США'],
    'america': ['США'],
    'united states of america': ['США'],
    'uk': ['Великобритания', 'Англия'],
    'united kingdom': ['Великобритания', 'Англия'],
    'britain': ['Великобритания', 'Англия'],
    'great britain': ['Великобритания', 'Англия'],
    'england': ['Англия'],
    'russia': ['Россия'],
    'russian federation': ['Россия'],
    'south africa': ['ЮАР'],
    'south korea': ['Корея,'],
    'korea': ['Корея,'],
    
    # Direct translations from countries.json
    'australia': ['Австралия'],
    'austria': ['Австрия'],
    'albania': ['Албания'],
    'alaska': ['Аляска'],
    'american samoa': ['Американское Самоа'],
    'anguilla': ['Ангилья'],
    'angola': ['Ангола'],
    'antarctica': ['Антарктида'],
    'antigua and barbuda': ['Антигуа и Барбуда'],
    'argentina': ['Аргентина'],
    'aruba': ['Аруба'],
    'bahamas': ['Багамские о-ва'],
    'balearic islands': ['Балеарские о-ва'],
    'barbados': ['Барбадос'],
    'bahrain': ['Бахрейн'],
    'belize': ['Белиз'],
    'belgium': ['Бельгия'],
    'bermuda': ['Бермудские острова'],
    'bulgaria': ['Болгария'],
    'bonaire': ['Бонэйр'],
    'brazil': ['Бразилия'],
    'british virgin islands': ['Британские Виргинские о-ва'],
    'brunei': ['Бруней'],
    'vanuatu': ['Вануату'],
    'hungary': ['Венгрия'],
    'virgin islands': ['Виргинские острова'],
    'vietnam': ['Вьетнам'],
    'hawaii': ['Гавайи'],
    'haiti': ['Гаити'],
    'gambia': ['Гамбия'],
    'ghana': ['Гана'],
    'guadeloupe': ['Гваделупа'],
    'guatemala': ['Гватемала'],
    'germany': ['Германия'],
    'guernsey': ['Гернси'],
    'gibraltar': ['Гибралтар'],
    'honduras': ['Гондурас'],
    'grenada': ['Гренада'],
    'greenland': ['Гренландия'],
    'greece': ['Греция'],
    'denmark': ['Дания'],
    'dominica': ['Доминика'],
    'dominican republic': ['Доминиканская Республика', 'Доминиканская республика'],
    'egypt': ['Египет'],
    'india': ['Индия'],
    'indonesia': ['Индонезия'],
    'jordan': ['Иордания'],
    'iran': ['Иран'],
    'ireland': ['Ирландия'],
    'iceland': ['Исландия'],
    'spain': ['Испания'],
    'italy': ['Италия'],
    'cape verde': ['Кабо-Верде'],
    'cayman islands': ['Каймановы острова'],
    'cambodia': ['Камбоджа'],
    'cameroon': ['Камерун'],
    'canada': ['Канада'],
    'canary islands': ['Канарские острова'],
    'qatar': ['Катар'],
    'cyprus': ['Кипр'],
    'china': ['Китай'],
    'colombia': ['Колумбия'],
    'costa rica': ['Коста-Рика'],
    'ivory coast': ['Кот-д\'Ивуар'],
    'curacao': ['Кюрасао'],
    'latvia': ['Латвия'],
    'lithuania': ['Литва'],
    'mauritius': ['Маврикий'],
    'madagascar': ['Мадагаскар'],
    'mayotte': ['Майотта'],
    'malaysia': ['Малайзия'],
    'maldives': ['Мальдивские о-ва'],
    'malta': ['Мальта'],
    'morocco': ['Марокко'],
    'martinique': ['Мартиника'],
    'mexico': ['Мексика'],
    'mozambique': ['Мозамбик'],
    'monaco': ['Монако'],
    'isle of man': ['Мэн, о-в'],
    'namibia': ['Намибия'],
    'netherlands': ['Нидерланды'],
    'nicaragua': ['Никарагуа'],
    'niue': ['Ниуэ'],
    'new zealand': ['Новая Зеландия'],
    'new caledonia': ['Новая Каледония'],
    'norway': ['Норвегия'],
    'oman': ['Оман'],
    'saint barthelemy': ['Остров Святого Варфоломея'],
    'cook islands': ['Острова Кука'],
    'pitcairn islands': ['Острова Питкэрн'],
    'pakistan': ['Пакистан'],
    'panama': ['Панама'],
    'papua new guinea': ['Папуа - Новая Гвинея'],
    'peru': ['Перу'],
    'poland': ['Польша'],
    'portugal': ['Португалия'],
    'puerto rico': ['Пуэрто-Рико'],
    'reunion': ['Реюньон'],
    'romania': ['Румыния'],
    'el salvador': ['Сальвадор'],
    'samoa': ['Самоа'],
    'sao tome and principe': ['Сан-Томе и Принсипе'],
    'saudi arabia': ['Саудовская Аравия'],
    'svalbard and jan mayen': ['Свальбард и Ян-Майен'],
    'seychelles': ['Сейшельские Острова'],
    'saint martin': ['Сен-Мартен'],
    'saint pierre and miquelon': ['Сен-Пьер и Микелон'],
    'senegal': ['Сенегал'],
    'saint vincent and the grenadines': ['Сент-Винсент и Гренадины'],
    'saint kitts and nevis': ['Сент-Китс и Невис'],
    'saint lucia': ['Сент-Люсия'],
    'serbia': ['Сербия'],
    'singapore': ['Сингапур'],
    'slovakia': ['Словакия'],
    'slovenia': ['Словения'],
    'solomon islands': ['Соломонские острова'],
    'taiwan': ['Тайвань'],
    'thailand': ['Тайланд'],
    'turks and caicos': ['Теркс и Кайкос'],
    'togo': ['Того'],
    'tonga': ['Тонга'],
    'trinidad and tobago': ['Тринидад и Тобаго'],
    'tunisia': ['Тунис'],
    'turkey': ['Турция'],
    'uruguay': ['Уругвай'],
    'faroe islands': ['Фарерские о-ва'],
    'fiji': ['Фиджи'],
    'philippines': ['Филиппины', 'Филиппинские острова'],
    'finland': ['Финляндия'],
    'florida': ['Флорида'],
    'falkland islands': ['Фолклендские острова'],
    'france': ['Франция'],
    'french guiana': ['Французская Гвиана'],
    'french polynesia': ['Французская Полинезия'],
    'croatia': ['Хорватия'],
    'montenegro': ['Черногория'],
    'czech republic': ['Чехия'],
    'chile': ['Чили'],
    'switzerland': ['Швейцария'],
    'sweden': ['Швеция'],
    'scotland': ['Шотландия'],
    'sri lanka': ['Шри-Ланка'],
    'ecuador': ['Эквадор'],
    'estonia': ['Эстония'],
    'jamaica': ['Ямайка'],
    'japan': ['Япония'],
}

def get_country_id(country_name: str):
    """Get country ID by name with alternative name mapping."""
    try:
        countries = _get_countries_data()
        if not countries:
            return None

        country_lower = country_name.lower().strip()
        
        # Get Russian alternatives for this country
        russian_names = COUNTRY_MAPPINGS.get(country_lower, [])
        
        # Try exact matches with Russian alternatives
        for russian_name in russian_names:
            for country in countries:
                if russian_name.lower() == country['text'].lower():
                    return country['id']
        
        # Fallback: translate input and try matching
        country_ru = _translate_to_russian(country_name)
        for country in countries:
            if country_ru.lower() in country['text'].lower():
                return country['id']

        return None

    except Exception as e:
        logger.error(f"Error in get_country_id: {e}")
        return None

def _translate_to_russian(text: str) -> str:
    """Translate text to Russian using Google Translate API."""
    try:
        import urllib.parse
        encoded_text = urllib.parse.quote(text)
        url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=ru&dt=t&q={encoded_text}"
        
        response = requests.get(url)
        if response.status_code == 200:
            result = response.json()
            return result[0][0][0] if result and result[0] and result[0][0] else text
        return text
    except:
        return text

def _get_countries_data():
    """Load countries data from API or cache."""
    try:
        base_url = os.getenv('CRUISE_API_BASE_URL', 'http://uat.center.cruises')
        response = requests.get(base_url + "/api/filter/cruise-countries.json")
        return response.json() if response.status_code == 200 else []
    except Exception as e:
        logger.error(f"Error in _get_countries_data: {e}")
        return []

if __name__ == "__main__":
    print(get_country_id("Angola"))
