from textual.widget import Widget
from textual.containers import Vertical
from textual.widgets import Label


class TextCardInfoWidget(Widget):
    CSS_PATH = "styles.tcss"

    def __init__(self, card_info: dict, **kwargs):
        super().__init__(**kwargs)
        self.card_info = card_info

    def compose(self):
        yield Vertical(
            Label(f"ID: {self.card_info['id']}"),
            Label(f"Type: {self.card_info['type']}"),
            Label(f"Scraper ID: {self.card_info['scraperId']}"),
            Label(f"Name: {self.card_info['name']}"),
            Label(f"Set Name: {self.card_info['set_name']}"),
            Label(f"URL: {self.card_info['url']}"),
            Label(f"Price: {self.card_info['price']} {self.card_info['currency']}"),
            Label(f"Foil: {self.card_info['foil']}"),
            Label(f"In Stock: {self.card_info['inStock']}", classes="in-stock"),
            Label(f"Stock: {self.card_info['stock']}", classes="stock"),
            Label(f"Borderless: {self.card_info['borderless']}"),
            Label(f"Condition: {self.card_info['condition']}"),
            id="card-info-container",
        )

    class Meta:
        css_class = "card-info-widget"
