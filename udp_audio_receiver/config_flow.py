import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from . import DOMAIN

class AudioReceiverFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return OptionsFlowHandler(config_entry)

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="Audio Receiver", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("host", default="0.0.0.0"): str,
                    vol.Required("port", default=12345): int,
                    vol.Required("save_path", default="/media/audio"): str,
                }
            ),
        )

class OptionsFlowHandler(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required("host", default=self.config_entry.options.get("host", "0.0.0.0")): str,
                    vol.Required("port", default=self.config_entry.options.get("port", 12345)): int,
                    vol.Required("save_path", default=self.config_entry.options.get("save_path", "/media/audio")): str,
                }
            ),
        )
