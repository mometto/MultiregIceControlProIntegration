from pymodbus.client.sync import ModbusTcpClient
from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import HVACMode
from homeassistant.const import TEMP_CELSIUS

CLIMATE_TYPES = {
    "setpoint_zone_1": {"register": 30005},  # Target temperature for Zone 1
    "setpoint_zone_2": {"register": 30006},
}

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Multireg IceControl climate controls."""
    host = config[CONF_HOST]
    port = config[CONF_PORT]

    client = ModbusTcpClient(host, port)

    climates = []
    for climate_name, props in CLIMATE_TYPES.items():
        climates.append(MultiregClimate(client, climate_name, props["register"]))

    add_entities(climates, True)

class MultiregClimate(ClimateEntity):
    """Representation of a temperature control unit."""

    def __init__(self, client, name, register):
        self._client = client
        self._name = name
        self._register = register
        self._target_temperature = None

    @property
    def name(self):
        return f"Multireg {self._name}"

    @property
    def hvac_modes(self):
        return [HVACMode.OFF, HVACMode.HEAT]

    @property
    def temperature_unit(self):
        return TEMP_CELSIUS

    @property
    def target_temperature(self):
        return self._target_temperature

    def set_temperature(self, **kwargs):
        """Set new target temperature."""
        temp = int(kwargs.get("temperature"))
        self._client.write_register(self._register, temp, unit=1)
        self._target_temperature = temp

    def update(self):
        """Fetch the current temperature setting."""
        result = self._client.read_holding_registers(self._register, 1, unit=1)
        if result.isError():
            _LOGGER.error("Modbus read error for register %s", self._register)
        else:
            self._target_temperature = result.registers[0]
