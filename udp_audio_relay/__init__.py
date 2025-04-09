import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN
from .relay import UDPAudioRelay

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict):
    conf = config.get(DOMAIN)
    if conf is not None:
        _LOGGER.info("Loading UDP Audio Relay from YAML config")
        hass.async_create_task(
            hass.config_entries.flow.async_init(
                DOMAIN,
                context={"source": "import"},
                data=conf
            )
        )
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Handle config entries (UI or YAML-imported)."""
    host = entry.data.get("host")
    port = entry.data.get("port")
    discovery_port = entry.data.get("discovery_port")
    discovery_keyword = entry.data.get("discovery_keyword")
    save_path = entry.data.get("save_path")

    udp_audio_relay = UDPAudioRelay(hass, host, port, discovery_port, discovery_keyword, save_path)
    await udp_audio_relay.start()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = udp_audio_relay
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Tear down on unload."""
    udp_audio_relay = hass.data[DOMAIN].pop(entry.entry_id)
    await udp_audio_relay.stop()
    return True