from homeassistant import config_entries
import voluptuous as vol
from .const import DOMAIN

class UDPAudioRelayConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the user step."""
        if user_input is not None:
            return self.async_create_entry(title="UDP Audio Relay", data=user_input)

        schema = vol.Schema({
            vol.Required("host", default="0.0.0.0"): str,
            vol.Required("port", default=12345): int,
            vol.Required("discovery_port", default=54321): int,
            vol.Required("discovery_keyword", default="HELLO_UDP_AUDIO_RELAY"): str,
            vol.Optional("save", default=False): bool,
            vol.Optional("save_path", default="/media/audio"): str,
            
        })

        return self.async_show_form(step_id="user", data_schema=schema)

    async def async_step_import(self, user_input=None):
        """Handle the import step (e.g., importing configuration)."""
        if user_input is not None:
            # Process imported data, such as loading it from YAML or another source
            return self.async_create_entry(title="Imported UDP Audio Relay", data=user_input)

        # If no input is provided, show the form for import configuration (if applicable)
        import_schema = vol.Schema({
            vol.Required("host", default="0.0.0.0"): str,
            vol.Required("port", default=12345): int,
            vol.Required("discovery_port", default=54321): int,
            vol.Required("discovery_keyword", default="HELLO_UDP_AUDIO_RELAY"): str,
        })

        return self.async_show_form(step_id="import", data_schema=import_schema)