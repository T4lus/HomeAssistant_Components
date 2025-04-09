from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN

class UDPAudioRelayConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="UDP Audio Relay", data=user_input)

        schema = vol.Schema({
            vol.Required("host", default="0.0.0.0"): str,
            vol.Required("port", default=12345): int,
            vol.Required("discovery_port", default=54321): int,
            vol.Required("discovery_keyword", default="HELLO_UDP_AUDIO_RELAY"): str,
            vol.Required("save_path", default="/media/audio"): str,
            
        })

        return self.async_show_form(step_id="user", data_schema=schema)