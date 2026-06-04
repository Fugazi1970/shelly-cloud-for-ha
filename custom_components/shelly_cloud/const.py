DOMAIN = "shelly_cloud"

CONF_AUTH_KEY = "auth_key"
CONF_SERVER_URL = "server_url"

# Polling-Intervall in Sekunden (mind. 1s wegen Rate Limit)
DEFAULT_SCAN_INTERVAL = 30

PLATFORMS = ["switch", "cover", "light"]

# Shelly-Gerätecodes -> Plattformen
# Gen1 Codes
SWITCH_CODES = {
    "SHSW-1", "SHSW-21", "SHSW-25", "SHSW-44", "SHSW-L",
    "SHPLG-S", "SHPLG-U1", "SHPLG2-1",
    "SHEM", "SHEM-3",
    "SHUNI-1",
    # Gen2/3
    "SNSW-001X16EU", "SNSW-002X16EU", "SNSW-001X8EU",
    "SPSW-001XE16EU", "SPSW-002XE16EU",
    "SNPL-00112EU", "SNPL-00116EU",
}

COVER_CODES = {
    "SHBLB-1", "SHCL-0",
    "SNSN-0013US",  # Gen2 Shutter
    "SNSH-01BE230",
}

LIGHT_CODES = {
    "SHBDUO-1", "SHCB-1", "SHDM-1", "SHDM-2",
    "SHRGBW2", "SHRGBW2-COLOR", "SHRGBW2-WHITE",
    "SHBTN-1", "SHBTN-2",
    "SNBU-09B", "SNDM-00100EU",
}
