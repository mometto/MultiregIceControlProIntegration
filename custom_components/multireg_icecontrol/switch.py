import logging
from pymodbus.client.sync import ModbusTcpClient
from homeassistant.components.switch import SwitchEntity
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

_LOGGER = logging.getLogger(__name__)

CONF_HOST = "host"
CONF_PORT = "port"

SWITCH_TYPES = {
    "heat_zone_1": {"register": 30003},  # Register to control heating for Zone 1
    "heat_zone_2": {"register": 30004},
}

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Multireg IceControl switches."""
    host = config[CONF_HOST]
    port = config[CONF_PORT]
    
    client = ModbusTcpClient(host, port)
    
    switches = []
    for switch_name, props in SWITCH_TYPES.items():
        switches.append(MultiregSwitch(client, switch_name, props["register"]))
    
    add_entities(switches, True)

class MultiregSwitch(SwitchEntity):
    """Representation of a controllable switch (heating on/off)."""

    def __init__(self, client, name, register):
        self._client = client
        self._name = name
        self._register = register
        self._state = None

    @property
    def name(self):
        return f"Multireg {self._name}"

    @property
    def is_on(self):
        return self._state == 1

    def turn_on(self, **kwargs):
        """Turn on the heating zone."""
        self._client.write_register(self._register, 1, unit=1)
        self._state = 1

    def turn_off(self, **kwargs):
        """Turn off the heating zone."""
        self._client.write_register(self._register, 0, unit=1)
        self._state = 0

    def update(self):
        """Fetch the current state from the Modbus device."""
        result = self._client.read_holding_registers(self._register, 1, unit=1)
        if result.isError():
            _LOGGER.error("Modbus read error for register %s", self._register)
        else:
            self._state = result.registers[0]
