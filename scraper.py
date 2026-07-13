import requests
from bs4 import BeautifulSoup
import json
import time

URL = 'https://www.e-korepetycje.net/uczen'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

DISCORD_WEBHOOK_URL = 'https://discord.com/api/webhooks/1526194231969054771/cWZaWEO5nSZPLSp5o-QPP1P_n8mJ_20NJGuhjA-pjVYtkW9UGwtL9nC0eVpORQnx3z69'


def get_latest_request():
    response = requests.get(URL, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'html.parser')

    css_path = '.content .main-container .content-wrapper .offer-list-container .offer-large'
    latest_ad = soup.select_one(css_path)

    if not latest_ad:
        return None

    offer_content = latest_ad.find('div', class_='offer-content')
    if not offer_content:
        return None

    def get_text_safe(element):
        return element.text.strip() if element else "N/A"

    offer_data = {
        "subject": get_text_safe(offer_content.find('span', class_='subject')),
        "name": get_text_safe(offer_content.find('h3')),
        "description": get_text_safe(offer_content.find('p')),
        "location": get_text_safe(offer_content.find('span', class_='offer-location')),
        "price": get_text_safe(offer_content.find('span', class_='lesson-price')),
        "time_detail": get_text_safe(offer_content.find('span', class_='lesson-time')),
        "date_added": get_text_safe(offer_content.find('div', class_='stopwatch-icon'))
    }

    if "Data dodania:" in offer_data["date_added"]:
        offer_data["date_added"] = offer_data["date_added"].replace("Data dodania:", "").strip().split('\xa0')

    return offer_data


def send_discord_alert(offer):
    """Sends a nicely formatted message to your Discord server."""
    message = f"🚨 **Nowe Ogłoszenie: {offer['subject']}** 🚨\n"
    message += f"**Od:** {offer['name']}\n"
    message += f"**Lokalizacja:** {offer['location']}\n"
    message += f"**Cena:** {offer['price']} {offer['time_detail']}\n\n"
    message += f"> {offer['description']}"

    # send to discord
    payload = {"content": message}
    requests.post(DISCORD_WEBHOOK_URL, json=payload)


def check_for_updates():
    latest_ad = get_latest_request()

    if not latest_ad:
        print("Couldn't find any ads. The website layout might have changed.")
        return

    try:
        with open('last_seen.json', 'r', encoding='utf-8') as file:
            last_seen_ad = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        last_seen_ad = {}

    if latest_ad.get('description') != last_seen_ad.get('description'):
        print("New offer detected!")

        # if latest_ad['subject'].lower() in ['matematyka', 'biologia']:
        #     send_discord_alert(latest_ad)

        with open('last_seen.json', 'w', encoding='utf-8') as file:
            json.dump(latest_ad, file, ensure_ascii=False, indent=4)

    else:
        print("No new requests. Checking again later...")


if __name__ == "__main__":
    check_for_updates()
