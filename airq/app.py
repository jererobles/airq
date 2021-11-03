import json
from datetime import datetime
import rumps

from AppKit import NSAttributedString
from PyObjCTools.Conversion import propertyListFromPythonCollection
from Cocoa import (NSFont, NSFontAttributeName,
                   NSColor, NSForegroundColorAttributeName)

from airq import consts

class App(rumps.App):
    def __init__(self, api):
        super().__init__(consts.LOADING_ICON)
        self.api = api
        self.last_data = None
        for key in consts.LABELS:
            if key == consts.KEY_SEPARATOR:
                self.menu.add(rumps.separator)
            else:
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
        self.last_data = api_response["data"]
        if not self.last_data:
            # API error
            self.title = consts.ERROR_ICON
            return
        self.update_status(self.last_data)

    def update_status(self, data):
        # warning icons
        new_icon = None
        for key, icons in consts.WARN_ICONS.items():
            value = (
                data[0][key] if isinstance(data[0][key], int) else data[0][key]["value"]
            )
            for rang, icon in icons.items():
                if rang[0] < value < rang[1]:
                    if new_icon in (None, consts.GOOD_ICON):
                        new_icon = icon
                    if icon == consts.GOOD_ICON:
                        self.warns.discard(key)
                    else:
                        self.warns.add(key)
                    break

        # sensor values
        values = data[0]
        formatted_values = {}
        warning_values = []
        for key, label in consts.LABELS.items():
            warningColor = None
            if key == consts.KEY_SEPARATOR:
                continue
            elif key == consts.KEY_LASTFETCH:
                value = datetime.now()
            elif key == consts.KEY_TIMESTAMP:
                value = datetime.fromtimestamp(values[key])
            elif not isinstance(values[key], int):
                value = values[key]["value"]
                warningColor = values[key]["color"]
            else:
                value = values[key]

            if key == consts.KEY_TEMP:
                new_title = label.format(value, (value - 32) / 1.8)
            else:
                new_title = label.format(value)
            self.menu[key].title = new_title
            formatted_values[key] = new_title

            if warningColor == 'yellow':
                color = NSColor.colorWithCalibratedRed_green_blue_alpha_(204/255, 204/255, 0, 1)
                font = NSFont.fontWithName_size_("Courier-Bold", 14.0)
                warning_values = warning_values + [new_title]
            elif warningColor == 'red':
                color = NSColor.colorWithCalibratedRed_green_blue_alpha_(1, 0, 0, 1)
                font = NSFont.fontWithName_size_("Courier-Bold", 14.0)
                warning_values = [new_title] + warning_values
            else:
                color = NSColor.colorWithCalibratedRed_green_blue_alpha_(0, 186.0/255, 44.0/255, 1)
                font = NSFont.fontWithName_size_("Courier", 14.0)

            attributes = propertyListFromPythonCollection({
                NSFontAttributeName: font,
                NSForegroundColorAttributeName: color}
                , conversionHelper=lambda x: x)
            string = NSAttributedString.alloc().initWithString_attributes_(new_title, attributes)
            self.menu[key]._menuitem.setAttributedTitle_(string)

        # use the major changers as the second info
        warned_sensor = formatted_values[consts.KEY_DUST].replace(" ", "")
        if warning_values:
            warned_sensor = warning_values[0].replace(" ", "")

        title_format = consts.DEFAULT_TITLE_FORMAT
        self.title = title_format.format(
            icon=new_icon,
            temp=self.strip_sensor_name(formatted_values[consts.KEY_TEMP].replace(" ", "").split("/")[0]),
            hisensor=self.strip_sensor_name(warned_sensor)
        )
            
    @rumps.clicked("Debug")
    def debug(self, sender):
        rumps.Window(
            title="AirQ Debug",
            default_text=json.dumps(self.last_data, indent=1),
            dimensions=(600, 800),
        ).run()

    def strip_sensor_name(self, formatted_value):
        return (" ".join(formatted_value.split(" ")[-2:])).replace(" ", "")
