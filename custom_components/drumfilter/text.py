"""Text platform for DrumFilter integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.text import TextEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import EntityCategory

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up DrumFilter text based on a config entry."""
    _LOGGER.debug("Setting up DrumFilter text entity")
    
    data = hass.data[DOMAIN][entry.entry_id]
    api = data["api"]
    
    texts = [
        DrumFilterNameText(api),
    ]
    
    async_add_entities(texts, True)
    _LOGGER.debug("DrumFilter text setup completed")

class DrumFilterNameText(TextEntity):
    """Representation of a DrumFilter name text entity."""

    def __init__(self, api) -> None:
        """Initialize the text entity."""
        self._api = api
        self._attr_name = "设备名称"
        self._attr_unique_id = f"{api.device_identifier}_name"
        self._attr_icon = "mdi:rename-box"
        self._attr_device_info = api.get_device_info()
        
        # 文本实体属性
        self._attr_native_max_length = 50  # 最大长度
        self._attr_mode = "text"  # 文本模式
        self._attr_pattern = None  # 无格式限制
        
        # 设置为配置类别，隐藏于首页，显示在设置中
        self._attr_entity_category = EntityCategory.CONFIG

    async def async_update(self) -> None:
        """Fetch new state data for the text entity."""
        try:
            await self._api.async_get_data()
            self._attr_native_value = self._api.device_info.get("name", "Unknown Device")
        except Exception as err:
            _LOGGER.error("Error updating name text: %s", err)
            self._attr_native_value = "Unknown Device"

    async def async_set_value(self, value: str) -> None:
        """Update the current value."""
        try:
            _LOGGER.debug("Setting device name to: %s", value)
            success = await self._api.async_control_device(name=value)
            if success:
                self._attr_native_value = value
                self.async_write_ha_state()
                _LOGGER.info("Device name updated to: %s", value)
            else:
                _LOGGER.error("Failed to set device name")
        except Exception as err:
            _LOGGER.error("Error setting device name: %s", err)