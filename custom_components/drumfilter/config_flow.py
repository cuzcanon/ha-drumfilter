"""Config flow for DrumFilter integration."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_TOKEN
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_TOKEN): str,
    }
)

async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    
    websession = async_get_clientsession(hass)
    
    try:
        timeout = aiohttp.ClientTimeout(total=10)
        response = await websession.post(
            "https://cuzcanon.cn/api/querybytoken",
            json={"token": data[CONF_TOKEN]},
            headers={"Content-Type": "application/json"},
            timeout=timeout
        )
        
        if response.status != 200:
            raise Exception(f"HTTP error: {response.status}")
            
        result = await response.json()
        
        # 更宽松的验证，只要有响应就认为有效
        if not result:
            raise Exception("Empty response from API")
            
        device_name = result.get("name", "DrumFilter")
        return {"title": device_name}
        
    except aiohttp.ClientError as err:
        raise Exception(f"Cannot connect to DrumFilter API: {err}")
    except Exception as err:
        raise Exception(f"Invalid token or API error: {err}")

class DrumFilterConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for DrumFilter."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
                
                await self.async_set_unique_id(user_input[CONF_TOKEN])
                self._abort_if_unique_id_configured()
                
                return self.async_create_entry(
                    title=info["title"], 
                    data=user_input
                )
                
            except Exception as err:
                errors["base"] = str(err)

        return self.async_show_form(
            step_id="user", 
            data_schema=STEP_USER_DATA_SCHEMA, 
            errors=errors
        )