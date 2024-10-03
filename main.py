import asyncio
from typing import Coroutine
from textual.app import App, ComposeResult
from textual.events import Key
from textual.widgets import Static, Button, Header, Label, RichLog, Input
from textual.css.query import NoMatches  # Import NoMatches exception

from magicmargins import (
    fetch_search_cards,
    get_card_uuid,
    fetch_mm_scrapers_list,
    fetch_seller_info,
    format_seller_info,
)
from card_info_widget import CardInfoWidget  # Import the custom widget


class MyApp(App):
    CSS_PATH = "styles.tcss"
    TITLE = "Magic Search"
    SUB_TITLE = "Canada Magic Cards Search App"

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(
            """
_______  _______  _______ _________ _______    _______  _______  _______  _______  _______          
(       )(  ___  )(  ____ \\__   __/(  ____ \  (  ____ \(  ____ \(  ___  )(  ____ )(  ____ \|\     /|
| () () || (   ) || (    \/   ) (   | (    \/  | (    \/| (    \/| (   ) || (    )|| (    \/| )   ( |
| || || || (___) || |         | |   | |        | (_____ | (__    | (___) || (____)|| |      | (___) |
| |(_)| ||  ___  || | ____    | |   | |        (_____  )|  __)   |  ___  ||     __)| |      |  ___  |
| |   | || (   ) || | \_  )   | |   | |              ) || (      | (   ) || (\ (   | |      | (   ) |
| )   ( || )   ( || (___) |___) (___| (____/\  /\____) || (____/\| )   ( || ) \ \__| (____/\| )   ( |
|/     \||/     \|(_______)\_______/(_______/  \_______)(_______/|/     \||/   \__/(_______/|/     \|
""",
            id="main-title",
        )
        yield Label("Press enter to submit")
        yield Input(placeholder="Enter card name...", id="card-input")
        yield RichLog(id="log")

    def _on_key(self, event: Key) -> None:
        print(f"Key event: {event}")  # Debugging statement
        self.query_one(RichLog).write(event)

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        card_name = event.value
        print(f"Input submitted: {card_name}")  # Debugging statement
        self.query_one(RichLog).write(f"Card name entered: {card_name}")

        # Create a task for the main program to keep the UI responsive
        asyncio.create_task(self.run_main_program(card_name))

    async def run_main_program(self, card_name: str) -> None:
        try:
            # Outputs dict
            self.query_one(RichLog).write("Fetching search cards...")
            search_cards_result = await asyncio.to_thread(fetch_search_cards, card_name)
            self.query_one(RichLog).write(f"Fetch_search_cards: {search_cards_result}")

            search_cards_id = []
            for i in search_cards_result:
                self.query_one(RichLog).write(f"Getting card UUID for: {i}")
                x = await asyncio.to_thread(get_card_uuid, i)
                search_cards_id.append(x)

            for card_id in search_cards_id:
                for scraper in fetch_mm_scrapers_list():
                    self.query_one(RichLog).write(
                        f"Fetching seller info for card ID: {card_id} with scraper: {scraper}"
                    )
                    seller_info = await asyncio.to_thread(
                        fetch_seller_info, card_id, scraper
                    )
                    # self.query_one(RichLog).write(seller_info)
                    if seller_info and int(seller_info[0]["stock"]) > 0:
                        self.query_one(RichLog).write(f"{seller_info}")
                        card_info_widget = CardInfoWidget(seller_info[0])
                        self.mount(card_info_widget)
                    else:
                        self.query_one(RichLog).write(f"{scraper} out of stock")
        except asyncio.CancelledError:
            try:
                self.query_one(RichLog).write("Task was cancelled")
            except NoMatches:
                print("Task was cancelled and RichLog widget is not available")


if __name__ == "__main__":
    app = MyApp()
    try:
        app.run()
    except KeyboardInterrupt:
        print("Application interrupted by user")
