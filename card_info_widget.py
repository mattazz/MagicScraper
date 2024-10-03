from textual.widget import Widget
from rich.panel import Panel
from rich.text import Text


class CardInfoWidget(Widget):
    CSS_PATH = "styles.tcss"

    def __init__(self, card_info: dict, **kwargs):
        super().__init__(**kwargs)
        self.card_info = card_info

    def render(self) -> Panel:
        card_details = Text()
        card_details.append(f"ID: {self.card_info['id']}\n")
        card_details.append(f"Type: {self.card_info['type']}\n")
        card_details.append(f"Scraper ID: {self.card_info['scraperId']}\n")
        card_details.append(f"Name: {self.card_info['name']}\n")
        card_details.append(f"Set Name: {self.card_info['set_name']}\n")
        card_details.append(f"URL: {self.card_info['url']}\n")
        card_details.append(
            f"Price: {self.card_info['price']} {self.card_info['currency']}\n"
        )
        card_details.append(f"Foil: {self.card_info['foil']}\n")

        # Add styling to "In Stock" and "Stock"
        card_details.append("In Stock: ", style="bold green")
        card_details.append(f"{self.card_info['inStock']}\n", style="bold green")
        card_details.append("Stock: ", style="bold blue")
        card_details.append(f"{self.card_info['stock']}\n", style="bold blue")

        card_details.append(f"Borderless: {self.card_info['borderless']}\n")
        card_details.append(f"Condition: {self.card_info['condition']}\n")

        return Panel(card_details, title="Card Information", padding=(0, 1))
