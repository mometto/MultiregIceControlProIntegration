import logging
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.discovery import load_platform
from homeassistant.const import CONF_NAME, CONF_HOST, CONF_PORT
import voluptuous as vol

DOMAIN = "multireg_icecontrol"

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_NAME, default="Multireg IceControl"): cv.string,
                vol.Required(CONF_HOST): cv.string,
                vol.Required(CONF_PORT, default=502): cv.port
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)

def setup(hass, config):
    """Set up the Multireg IceControl component."""
    conf = config[DOMAIN]
    hass.data[DOMAIN] = {
        "name": conf.get(CONF_NAME),
        "host": conf.get(CONF_HOST),
        "port": conf.get(CONF_PORT),
    }

    load_platform(hass, "sensor", DOMAIN, {}, config)
    return True
