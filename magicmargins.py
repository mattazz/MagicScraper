import requests
import json
import utils

# https://magicmargins.ca/v1/cards?search=heartfire&sparse=true


def fetch_search_cards(search: str) -> dict:
    """
    Gets the list of cards based on the search query. Includes Name, Date Released, and card ID
    to be used for magicmargins API in getting card shop scrapes.

    Args:
        search (str): The search query string.

    Returns:
        dict: A dict of cards with their details.
    """

    url = f"https://magicmargins.ca/v1/cards?search={search}&sparse=false"
    response = requests.get(url)
    if response.status_code == 200:
        try:
            res = response.json()
            return res["cards"]
        except requests.exceptions.JSONDecodeError:
            print(f"No JSON content returned for {search}")
            return None
    else:
        print(f"Failed to fetch data for {search}: {response.status_code}")
        return None


def fetch_full_card_details(card_names: list) -> list:
    """
    Fetches the full metadata for a list of card names, including image URLs.

    Args:
        card_names (list): A list of card names.

    Returns:
        list: A list of dicts containing the full metadata for each card.
    """
    url = "https://magicmargins.ca/v1/cards"
    payload = {"cardNames": card_names, "unique": True}
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        try:
            return response.json()
        except requests.exceptions.JSONDecodeError:
            print(f"No JSON content returned for {card_names}")
            return None
    else:
        print(
            f"Failed to fetch full card details for {card_names}: {response.status_code}"
        )
        return None


def display_search_cards(searchList: dict) -> None:
    """
    Displays (in print) the name and release date of the cards from the query search

    Args:
        searchList (dict): The object from fetch_search_cards()

    Returns:
        None
    """
    # The dict keys
    name = "key"
    date = "released_at"
    id = "id"

    utils.print_hash(20)
    for i in searchList:
        print(f"{i[name]} - {i['metadata'][date]} - {i['metadata'][id]}")
        utils.print_hash(max(len(i[name]), len(i["metadata"][date])) * 3)


def get_card_uuid(data: dict) -> str:
    """Simply gets the uuid from this format:\n
    {'key': 'Heartfire', 'metadata': {'id': '7db219ea-2ed1-4a86-955c-d61ecedbc019', 'released_at': '2019-05-03'}}

    Args:
        data (dict): must be not iterable

    Returns:
        str: the uuid
    """
    return data["metadata"]["id"]


# ex. 48ace959-66b2-40c8-9bff-fd7ed9c99a82
def fetch_specific_card(search_uuid: str) -> dict:
    """Fetches metadata of specific card based on card's uuid

    Args:
        search_uuid (str): Unique identified taken from fetch_search_cards

    Returns:
        dict: Specific card data
    """
    url = f"https://magicmargins.ca/v1/cards/{search_uuid}"
    response = requests.get(url)

    if response.status_code == 200:
        try:
            return response.json()
        except:
            print(f"Error: {response.text}")
            return None


def fetch_mm_scrapers_list() -> list:
    """Gets the list of scrapers IDs similar to this: \n
    {id: "facetofacegames", url: "https://www.facetofacegames.com", buylist: true, selllist: true}


    Returns:
        Example: ['facetofacegames', 'kanatacg', '401games', 'fusiongamingonline', 'kesselrungames', 'gamezilla', 'comichunter', 'multizone', 'cartamagica', 'cardshoptolaria', 'vortexgames', 'magicstronghold', 'everythinggames', 'gauntletgamesvictoria', 'gameknight', 'allaboardgames']
    """
    url = f"https://magicmargins.ca/v1/scrapers"
    response = requests.get(url)

    result_arr = []

    if response.status_code == 200:
        try:
            result = response.json()
            # print(result)
            if result is not None:
                for item in result:
                    result_arr.append(item["id"])

                # print(result_arr)
                return result_arr
            else:
                print("Error: No JSON Concent Returned")
                return None
        except requests.exceptions.JSONDecodeError:
            print(f"Error: {response.text}")
            return None
    else:
        print(f"Failed to fetch data:  {response.status_code}")
        return None


def fetch_seller_info(cardID: str, scraperID: str):
    """Gets seller info list, if it's in-stock, price etc.

    Args:
        cardID (str): id taken form card metadata from MM
        scraperID (str): Taken from fetch_mm_scrapers() 'id' \n
        {'id': 'facetofacegames', 'url': 'https://www.facetofacegames.com', 'buylist': True, 'selllist': True}

    Returns:
        _type_: _description_
    """

    url = f"https://magicmargins.ca/v1/scrapers/{scraperID}/scrape/{cardID}?ignore_sets=true"
    response = requests.get(url)

    if response.status_code == 200:
        try:
            return response.json()

        except:
            print(f"Error: {response.text}")
            return None


def format_seller_info(seller_info: list):
    """
    Formats the seller information in a readable way.\n
    This is just a pretty-print function

    Args:
        seller_info (list): A list of dictionaries containing seller information.
    """
    for info in seller_info:
        print(f"ID: {info['id']}")
        print(f"Type: {info['type']}")
        print(f"Scraper ID: {info['scraperId']}")
        print(f"Name: {info['name']}")
        print(f"Set Name: {info['set_name']}")
        print(f"URL: {info['url']}")
        print(f"Price: {info['price']} {info['currency']}")
        print(f"Foil: {info['foil']}")
        print(f"In Stock: {info['inStock']}")
        print(f"Stock: {info['stock']}")
        print(f"Borderless: {info['borderless']}")
        print(f"Condition: {info['condition']}")
        print("-" * 40)


def main():
    """Main function"""
    userInput = input("Search for a card: ")

    result = fetch_search_cards(userInput)
    print(result)

    arr_cards_id = []
    for i in result:
        x = get_card_uuid(i)
        arr_cards_id.append(x)

    for card_id in arr_cards_id:
        for scraper in fetch_mm_scrapers_list():
            seller_info = fetch_seller_info(card_id, scraper)
            # print(seller_info[0])
            if seller_info and int(seller_info[0]["stock"]) > 0:
                # format_seller_info(seller_info)
                print(seller_info)
            else:
                print(f"{scraper} out of")


# main()

scrapers = fetch_mm_scrapers_list()
print(f"Scrapers: {scrapers}")

for scraper in scrapers:
    print()
    res = fetch_seller_info("af482a14-a144-4e60-bd04-a548a3c89f5a", scraper)
    print(res)
