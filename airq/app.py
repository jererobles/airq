import json
from datetime import datetime
import rumps
from airq import consts


class App(rumps.App):
    def __init__(self, api):
        super(App, self).__init__("🏖️")
        self.api = api
        self.last_data = None
        for key in consts.LABELS:
            self.add_menu(key)
        self.menu.add(rumps.separator)
        self.add_menu("Refresh Now...")
        self.add_menu("Debug")
        self.warns = set()
        rumps.debug_mode(True)

    def add_menu(self, title):
        self.menu.add(rumps.MenuItem(title=title))

    @rumps.clicked("Refresh Now...")
    @rumps.timer(60 * 5)
    def refresh_data(self, sender):
        api_response = self.api.get_data()
        if not api_response:
            # HTTP error
            self.title = consts.ERROR_ICON
            return
        self.last_data = api_response.json()["data"]
        if not self.last_data:
            # API error
            self.title = consts.ERROR_ICON
            return
        self.update_icon(self.last_data)
        self.update_values(self.last_data)

    def update_icon(self, data):
        new_icon = None
        for key, icons in consts.WARN_ICONS.items():
            value = (
                data[0][key] if isinstance(data[0][key], int) else data[0][key]["value"]
            )
            for rang, icon in icons.items():
                if rang[0] < value < rang[1]:
                    if new_icon in (None, "☺️"):
                        new_icon = icon
                    self.warns.discard(key) if icon == "☺️" else self.warns.add(key)
                    break
        self.title = new_icon

    def update_values(self, data):
        values = data[0]
        for key, label in consts.LABELS.items():
            if key == consts.KEY_LASTFETCH:
                value = datetime.now()
            elif key == consts.KEY_TIMESTAMP:
                value = datetime.fromtimestamp(values[key])
            elif not isinstance(values[key], int):
                value = values[key]["value"]
            else:
                value = values[key]
            new_title = label.format(value) + ("  ⚠️" if key in self.warns else "")
            self.menu[key].title = new_title

    @rumps.clicked("Debug")
    def debug(self, sender):
        rumps.Window(
            title="AirQ Debug",
            default_text=json.dumps(self.last_data, indent=1),
            dimensions=(600, 800),
        ).run()
