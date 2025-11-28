"""The DrumFilter integration."""
from __future__ import annotations

import logging
from typing import Any
from datetime import timedelta

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_TOKEN
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN, API_QUERY, API_CONTROL

_LOGGER = logging.getLogger(__name__)

# 恢复 text 平台
PLATFORMS = ["sensor", "number", "scene", "text"]
DEFAULT_UPDATE_INTERVAL = 10

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up DrumFilter from a config entry."""
    _LOGGER.debug("Setting up DrumFilter integration")
    
    hass.data.setdefault(DOMAIN, {})
    
    try:
        api = DrumFilterAPI(hass, entry.data[CONF_TOKEN])
        
        coordinator = DrumFilterDataUpdateCoordinator(
            hass,
            api=api,
            update_interval=timedelta(seconds=DEFAULT_UPDATE_INTERVAL),
        )
        
        await coordinator.async_config_entry_first_refresh()
        
        hass.data[DOMAIN][entry.entry_id] = {
            "api": api,
            "coordinator": coordinator
        }

        await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
        _LOGGER.info("DrumFilter integration setup completed successfully")
        return True
        
    except Exception as ex:
        _LOGGER.error("Failed to setup DrumFilter integration: %s", ex)
        raise ConfigEntryNotReady(f"Could not connect to DrumFilter API: {ex}") from ex

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug("Unloading DrumFilter integration")
    
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok

class DrumFilterDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching DrumFilter data."""

    def __init__(self, hass: HomeAssistant, api, update_interval: timedelta) -> None:
        """Initialize."""
        self.api = api
        super().__init__(
            hass,
            _LOGGER,
            name="DrumFilter",
            update_interval=update_interval,
        )

    async def _async_update_data(self):
        """Fetch data from API."""
        return await self.api.async_get_data()

class DrumFilterAPI:
    """API for DrumFilter."""
    
    def __init__(self, hass: HomeAssistant, token: str) -> None:
        """Initialize the API."""
        self.hass = hass
        self.token = token
        self.websession = async_get_clientsession(hass)
        self.data = {}
        self.device_info = {
            "name": "Unknown",
            "interval": 0,
            "network": "unknown",
            "uid": "unknown",
            "model": "DrumFilter",
            "last_record": None,
            "total_records": 0
        }

    @property
    def device_identifier(self) -> str:
        """Return device unique identifier."""
        return self.device_info.get("uid", "unknown")

    def get_device_info(self) -> DeviceInfo:
        """Get Home Assistant device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.device_identifier)},
            name=self.device_info.get("name", "DrumFilter"),
            manufacturer="DrumFilter",
            model=self.device_info.get("model", "DrumFilter"),
        )

    async def async_get_data(self) -> dict[str, Any]:
        """Get data from the API."""
        _LOGGER.debug("Fetching data from API")
        
        try:
            timeout = aiohttp.ClientTimeout(total=10)
            response = await self.websession.post(
                API_QUERY,
                json={"token": self.token},
                headers={"Content-Type": "application/json"},
                timeout=timeout
            )
            
            if response.status != 200:
                raise Exception(f"HTTP error: {response.status}")
                
            data = await response.json()
            
            records = data.get("records", [])
            last_record = records[-1] if records else None
            
            self.device_info.update({
                "name": data.get("name", "DrumFilter"),
                "interval": data.get("interval", 10),
                "network": data.get("network", "offline"),
                "uid": data.get("uid", ""),
                "model": data.get("model", "DrumFilter"),
                "last_record": last_record,
                "total_records": len(records)
            })
            
            self.data = data
            return data
            
        except aiohttp.ClientError as err:
            _LOGGER.error("Network error fetching data: %s", err)
            raise
        except Exception as err:
            _LOGGER.error("Error fetching data: %s", err)
            raise

    async def async_control_device(self, interval: int | None = None, clean: bool = False, name: str | None = None) -> bool:
        """Send control command to device."""
        _LOGGER.debug("Sending control command: interval=%s, clean=%s, name=%s", interval, clean, name)
        
        try:
            uid = self.device_info.get("uid")
            if not uid:
                _LOGGER.error("No UID available for control command")
                return False
                
            payload = {
                "token": self.token,
                "uid": uid
            }
            
            if interval is not None:
                payload["interval"] = interval
            if clean:
                payload["clean"] = "true"
            if name is not None:
                payload["name"] = name
            
            timeout = aiohttp.ClientTimeout(total=10)
            response = await self.websession.post(
                API_CONTROL,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=timeout
            )
            
            if response.status != 200:
                _LOGGER.error("Control API returned error: %s", response.status)
                return False
                
            await response.json()
            return True
            
        except aiohttp.ClientError as err:
            _LOGGER.error("Network error controlling device: %s", err)
            return False
        except Exception as err:
            _LOGGER.error("Error controlling device: %s", err)
            return False