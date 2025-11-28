"""Sensor platform for DrumFilter integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import DOMAIN, CLEAN_REASON_MAP, NETWORK_STATUS_MAP

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up DrumFilter sensors based on a config entry."""
    _LOGGER.debug("Setting up DrumFilter sensors")
    
    data = hass.data[DOMAIN][entry.entry_id]
    api = data["api"]
    coordinator = data["coordinator"]
    
    sensors = [
        # 移除名称传感器，因为有可编辑的文本实体了
        # DrumFilterSensor(coordinator, api, "name", "设备名称", "mdi:rename-box"),
        DrumFilterSensor(coordinator, api, "network", "网络状态", "mdi:network"),
        DrumFilterSensor(coordinator, api, "last_record", "最近清洗", "mdi:history"),
    ]
    
    async_add_entities(sensors)
    _LOGGER.debug("DrumFilter sensors setup completed")

class DrumFilterSensor(CoordinatorEntity, SensorEntity):
    """Representation of a DrumFilter sensor."""

    def __init__(self, coordinator, api, sensor_type: str, sensor_name: str, icon: str) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._api = api
        self._sensor_type = sensor_type
        self._attr_name = sensor_name
        self._attr_unique_id = f"{api.device_identifier}_{sensor_type}"
        self._attr_icon = icon
        self._attr_device_info = api.get_device_info()

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None
            
        device_info = self._api.device_info
        
        if self._sensor_type == "network":
            network_status = device_info.get("network", "unknown")
            return NETWORK_STATUS_MAP.get(network_status, network_status)
                
        elif self._sensor_type == "last_record":
            last_record = device_info.get("last_record")
            if not last_record:
                return "暂无记录"
                
            timestamp = last_record.get("time")
            reason = last_record.get("reason", "unknown")
            
            if not timestamp:
                return f"时间未知 ({CLEAN_REASON_MAP.get(reason, reason)})"
            
            record_time = dt_util.utc_from_timestamp(timestamp)
            local_time = dt_util.as_local(record_time)
            time_str = local_time.strftime("%m-%d %H:%M")
            reason_text = CLEAN_REASON_MAP.get(reason, reason)
            
            return f"{time_str} {reason_text}"
        
        return None

    @property
    def extra_state_attributes(self):
        """Return additional attributes for the sensor."""
        if self._sensor_type != "last_record" or not self.coordinator.data:
            return None
            
        device_info = self._api.device_info
        last_record = device_info.get("last_record")
        
        if not last_record:
            return None
            
        return {
            "Reason": last_record.get("reason", "unknown"),
            "Timestamp": last_record.get("time"),
        }