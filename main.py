import asyncio
from typing import Coroutine
from textual.app import App, ComposeResult
from textual.events import Key
from textual.widgets import Static, Button, Header, Label, RichLog, Input, Pretty
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.css.query import NoMatches  # Import NoMatches exception

from utils import print_hash

from magicmargins import (
    fetch_search_cards,
    get_card_uuid,
    fetch_mm_scrapers_list,
    fetch_seller_info,
    format_seller_info,
)
from card_info_widget import CardInfoWidget  # Import the custom widget
from text_card_info_widget import TextCardInfoWidget

fancy_text_title = """
_______  _______  _______ _________ _______    _______  _______  _______  _______  _______          
(       )(  ___  )(  ____ \\__   __/(  ____ \  (  ____ \(  ____ \(  ___  )(  ____ )(  ____ \|\     /|
| () () || (   ) || (    \/   ) (   | (    \/  | (    \/| (    \/| (   ) || (    )|| (    \/| )   ( |
| || || || (___) || |         | |   | |        | (_____ | (__    | (___) || (____)|| |      | (___) |
| |(_)| ||  ___  || | ____    | |   | |        (_____  )|  __)   |  ___  ||     __)| |      |  ___  |
| |   | || (   ) || | \_  )   | |   | |              ) || (      | (   ) || (\ (   | |      | (   ) |
| )   ( || )   ( || (___) |___) (___| (____/\  /\____) || (____/\| )   ( || ) \ \__| (____/\| )   ( |
|/     \||/     \|(_______)\_______/(_______/  \_______)(_______/|/     \||/   \__/(_______/|/     \|
"""


class MyApp(App):
    CSS_PATH = "styles.tcss"
    TITLE = "Magic Search"
    SUB_TITLE = "Canada Magic Cards Search App"

    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            Vertical(
                Static(
                    "Magic Search",
                    id="main-title",
                ),
                Label("Press enter to submit"),
                Input(placeholder="Enter card name...", id="card-input"),
                RichLog(id="log"),
                id="left-panel",
            ),
            Vertical(id="right-panel"),
            id="main-container",
        )

    def _on_key(self, event: Key) -> None:
        print(f"Key event: {event}")  # Does nothing lol

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        self.query_one(RichLog).clear()
        card_name = event.value
        print(f"Input submitted: {card_name}")  # Debugging statement
        self.query_one(RichLog).write(f"Card name entered: {card_name}")

        # Create a task for the main program to keep the UI responsive
        asyncio.create_task(self.run_main_program(card_name))

    async def run_main_program(self, card_name: str) -> None:
        try:
            # Outputs dict
            self.query_one(RichLog).write("Fetching search cards...")
            search_cards_result: list = await asyncio.to_thread(
                fetch_search_cards, card_name
            )
            self.query_one(RichLog).write(f"Fetch_search_cards: {search_cards_result}")

            # Once you get the cards, you should display the cards for user to select the right UUID
            for result in search_cards_result:
                self.query_one(RichLog).write(f"Card: {result}")

            search_cards_id = []  # Only the ID
            for i in search_cards_result:
                self.query_one(RichLog).write(f"Getting card UUID for: {i}")
                x = await asyncio.to_thread(get_card_uuid, i)
                search_cards_id.append(x)

            # Layout Panels
            right_panel = self.query_one("#right-panel")

            ## For eventual button container
            max_buttons_per_row = 3
            current_row = Horizontal(classes="button-container")

            right_panel.mount(Label("Click on the correct card you wanted to search"))
            right_panel.mount(current_row)
            button_count = 0

            # Trying to display the list of Cards, and their UUIDs so users can click it

            for card in search_cards_result:
                try:
                    self.query_one(RichLog).write(
                        f"Adding button for card: {card['key']}"
                    )
                    button = Button(
                        label=f"{card['key']}",
                        id=f"button-{card['metadata']['id']}",
                        classes="button",
                    )
                    self.query_one(RichLog).write(f"Button created: {button}")
                    current_row.mount(button)
                    button_count += 1

                    if button_count >= max_buttons_per_row:
                        self.query_one(RichLog).write(
                            f"Mounting row with {button_count} buttons"
                        )
                        self.query_one(RichLog).write(f"Mounting in the right_panel")
                        current_row = Horizontal(classes="button-container")
                        right_panel.mount(current_row)
                        button_count = 0
                except Exception as e:
                    self.query_one(RichLog).write(f"Error adding button: {e}")

            if button_count > 0:
                self.query_one(RichLog).write(
                    f"Mounting last row with {button_count} buttons"
                )
                right_panel.mount(current_row)

            #### This triggers the search
            # await self.search_seller_stock(search_cards_id, right_panel)

        except asyncio.CancelledError:
            try:
                self.query_one(RichLog).write("Task was cancelled")
            except NoMatches:
                print("Task was cancelled and RichLog widget is not available")

    async def search_seller_stock(self, search_cards_id: list, panel):
        """Searches the list of UUIDs for seller price and info

        Args:
            search_cards_id (list): Taken from fetch_search_cards() which gets the list of cards and their
            metadata (including id)

            panel (textual.container): Textual Layout panel
        """
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
                    self.query_one(RichLog).write(str(Pretty(seller_info)))

                    panel.mount(Label(print_hash(20), classes="red"))

                    for k, v in seller_info[0].items():

                        match k:
                            case "stock":
                                label = Label(f"{k}: {v}", classes="green")
                                panel.mount(label)
                            case "inStock":
                                label = Label(f"{k}: {v}", classes="yellow")
                                panel.mount(label)
                            case "url":
                                label = Label(f"{k}: {v}", classes="purple")
                                panel.mount(label)
                            case _:
                                label = Label(f"{k}: {v}", classes="")
                                panel.mount(label)

                    panel.mount(Label(print_hash(20), classes="red"))

                    #### BROKEN due to height issue #####
                    ### I think it's the use of the Panel that auto has height to fill parent

                    # card_info_widget = CardInfoWidget(seller_info[0])
                    # right_panel.mount(card_info_widget)
                else:
                    self.query_one(RichLog).write(f"{scraper} out of stock")


if __name__ == "__main__":
    app = MyApp()
    try:
        app.run()
    except KeyboardInterrupt:
        print("Application interrupted by user")
