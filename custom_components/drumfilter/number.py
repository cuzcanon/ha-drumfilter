"""Number platform for DrumFilter integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up DrumFilter number based on a config entry."""
    _LOGGER.debug("Setting up DrumFilter number entity")
    
    data = hass.data[DOMAIN][entry.entry_id]
    api = data["api"]
    
    numbers = [
        DrumFilterIntervalNumber(api),
    ]
    
    async_add_entities(numbers, True)
    _LOGGER.debug("DrumFilter number setup completed")

class DrumFilterIntervalNumber(NumberEntity):
    """Representation of a DrumFilter interval number entity."""

    def __init__(self, api) -> None:
        """Initialize the number entity."""
        self._api = api
        self._attr_name = "清洗间隔"
        self._attr_unique_id = f"{api.device_identifier}_interval"
        self._attr_icon = "mdi:timer-cog"
        self._attr_device_info = api.get_device_info()
        
        # 数字实体属性
        self._attr_native_min_value = 10
        self._attr_native_max_value = 43200
        self._attr_native_step = 1
        self._attr_mode = NumberMode.BOX
        self._attr_native_unit_of_measurement = "分钟"
        
        # 移除 entity_category，这样就会显示在首页
        # self._attr_entity_category = EntityCategory.CONFIG

    async def async_update(self) -> None:
        """Fetch new state data for the number entity."""
        try:
            await self._api.async_get_data()
            self._attr_native_value = self._api.device_info.get("interval", 60)
        except Exception as err:
            _LOGGER.error("Error updating interval number: %s", err)
            self._attr_native_value = 60

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        try:
            _LOGGER.debug("Setting interval to: %s", value)
            success = await self._api.async_control_device(interval=int(value))
            if success:
                self._attr_native_value = value
                self.async_write_ha_state()
                _LOGGER.info("Interval updated to %s minutes", value)
            else:
                _LOGGER.error("Failed to set interval")
        except Exception as err:
            _LOGGER.error("Error setting interval: %s", err)