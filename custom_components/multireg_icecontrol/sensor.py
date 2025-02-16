import logging
from pymodbus.client.sync import ModbusTcpClient
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.helpers.entity import Entity
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

_LOGGER = logging.getLogger(__name__)

CONF_HOST = "host"
CONF_PORT = "port"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_PORT, default=502): cv.port
    }
)

SENSOR_TYPES = {
    "zone_1_heating": {"register": 119, "unit": "°C"},  # Heating status Zone 1
    "zone_2_heating": {"register": 120, "unit": "°C"},  # Heating status Zone 2
    "afterrun_zone_1": {"register": 121, "unit": "min"},  # After-run time
    "afterrun_zone_2": {"register": 122, "unit": "min"},
    "heating_time_zone_1": {"register": 106, "unit": "h"},
    "heating_time_zone_2": {"register": 107, "unit": "h"},
    "total_energy_zone_1": {"register": 108, "unit": "kWh"},
    "total_energy_zone_2": {"register": 109, "unit": "kWh"},
    "active_alarms": {"register": 123, "unit": ""},
    "uptime_hours": {"register": 180, "unit": "h"},
    "uptime_years": {"register": 181, "unit": "years"},
}

def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the Multireg IceControl sensors."""
    host = config[CONF_HOST]
    port = config[CONF_PORT]
    
    client = ModbusTcpClient(host, port)
    
    sensors = []
    for sensor_name, props in SENSOR_TYPES.items():
        sensors.append(MultiregSensor(client, sensor_name, props["register"], props["unit"]))
    
    add_entities(sensors, True)

class MultiregSensor(Entity):
    """Representation of a Multireg IceControl sensor."""

    def __init__(self, client, name, register, unit):
        self._client = client
        self._name = name
        self._register = register
        self._unit = unit
        self._state = None

    @property
    def name(self):
        return f"Multireg {self._name}"

    @property
    def state(self):
        return self._state

    @property
    def unit_of_measurement(self):
        return self._unit

    def update(self):
        """Fetch new state data from the device."""
        result = self._client.read_holding_registers(self._register, 1, unit=1)
        if result.isError():
            _LOGGER.error("Modbus read error")
        else:
            self._state = result.registers[0]
