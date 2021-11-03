KEY_CO = "co"
KEY_CO2 = "co2"
KEY_NO2 = "no2"
KEY_VOC = "voc"
KEY_DUST = "dust"
KEY_TEMP = "temp"
KEY_OZONE = "ozone"
KEY_PRESSURE = "pressure"
KEY_HUMIDITY = "humidity"
KEY_VIRUSSCORE = "virusScore"
KEY_TIMESTAMP = "timestamp"
KEY_LASTFETCH = "lastfetch"
KEY_SEPARATOR = "separator"

DEFAULT_TITLE_FORMAT = "{icon} {temp} / {co2}"

LABELS = {
    KEY_CO:         "      CO: {} ppm",
    KEY_CO2:        "     CO₂: {} ppm",
    KEY_NO2:        "     NO₂: {} ppb",
    KEY_VOC:        "    TVOC: {} ppb",
    KEY_DUST:       "    Dust: {} ug/m³",
    KEY_TEMP:       "    Temp: {:.1f}°F/{:.1f}°C",
    KEY_OZONE:      "   Ozone: {} ppb",
    KEY_PRESSURE:   "Pressure: {} hPa",
    KEY_HUMIDITY:   "Humidity: {}%",
    KEY_VIRUSSCORE: "   Virus: {}/10",
    KEY_TIMESTAMP:  "Measured: {:%H:%M:%S}",
    # KEY_LASTFETCH: "Retrieved {:%H:%M:%S}",
}

GOOD_ICON = "☺️"

LOADING_ICON = "⏳"

ERROR_ICON = "❌"

WARN_ICON = "⚠️"

WARN_ICONS = {
    KEY_CO: {
        (0, 35): GOOD_ICON,
        (36, 70): "😵",
        (71, 100): "☠️",
    },
    KEY_CO2: {
        (400, 850): GOOD_ICON,
        (851, 1500): "🤢",
        (1501, 2500): "😵",
    },
    KEY_HUMIDITY: {
        (10, 30): "🌵",
        (31, 50): GOOD_ICON,
        (51, 100): "💦",
    },
    KEY_VOC: {
        (0, 400): GOOD_ICON,
        (401, 800): "😷",
        (801, 1100): "😵",
    },
    KEY_DUST: {
        (0, 50): GOOD_ICON,
        (51, 100): "😷",
        (101, 200): "😵",
    },
    KEY_VIRUSSCORE: {
        (1, 5): GOOD_ICON,
        (6, 8): "🦠",
        (9, 10): "😵",
    },
    KEY_PRESSURE: {
        (600, 970): "😣",
        (971, 1030): GOOD_ICON,
        (1031, 1100): "😖",
    },
    KEY_NO2: {
        (0, 100): GOOD_ICON,
        (101, 250): "🫁",
        (250, 500): "😵",
    },
}
