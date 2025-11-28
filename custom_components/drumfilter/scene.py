"""Scene platform for DrumFilter integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.scene import Scene
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
    """Set up DrumFilter scene based on a config entry."""
    _LOGGER.debug("Setting up DrumFilter scene")
    
    data = hass.data[DOMAIN][entry.entry_id]
    api = data["api"]
    
    scenes = [
        DrumFilterCleanScene(api),
    ]
    
    async_add_entities(scenes)
    _LOGGER.debug("DrumFilter scene setup completed")

class DrumFilterCleanScene(Scene):
    """Representation of a DrumFilter clean scene."""

    def __init__(self, api) -> None:
        """Initialize the scene."""
        self._api = api
        self._attr_name = "立即清洗"
        self._attr_unique_id = f"{api.device_identifier}_clean_scene"
        self._attr_icon = "mdi:broom"
        self._attr_device_info = api.get_device_info()

    async def async_activate(self, **kwargs: Any) -> None:
        """Activate the scene."""
        try:
            _LOGGER.debug("Sending clean command via scene")
            success = await self._api.async_control_device(clean=True)
            if success:
                _LOGGER.info("清洗命令发送成功")
            else:
                _LOGGER.error("发送清洗命令失败")
        except Exception as err:
            _LOGGER.error("发送清洗命令时出错: %s", err)