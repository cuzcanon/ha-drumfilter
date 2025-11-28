"""Constants for the DrumFilter integration."""
DOMAIN = "drumfilter"

CONF_TOKEN = "token"

API_BASE_URL = "https://cuzcanon.cn/api"
API_QUERY = f"{API_BASE_URL}/querybytoken"
API_CONTROL = f"{API_BASE_URL}/control"

# 实体类型常量
ENTITY_TYPE_NAME = "name"
ENTITY_TYPE_NETWORK = "network"
ENTITY_TYPE_LAST_RECORD = "last_record"
ENTITY_TYPE_INTERVAL = "interval"
ENTITY_TYPE_CLEAN = "clean"

# 显示名称
DISPLAY_NAME = "设备名称"
DISPLAY_NETWORK = "网络状态"
DISPLAY_LAST_RECORD = "最近清洗"
DISPLAY_INTERVAL = "清洗间隔"
DISPLAY_CLEAN = "立即清洗"

# 图标
ICON_NAME = "mdi:rename-box"
ICON_NETWORK = "mdi:network"
ICON_LAST_RECORD = "mdi:history"
ICON_INTERVAL = "mdi:timer-cog"
ICON_CLEAN = "mdi:spray-bottle"

# 网络状态映射
NETWORK_STATUS_MAP = {
    "online": "在线",
    "offline": "离线"
}

# 清洗原因映射
CLEAN_REASON_MAP = {
    "timing": "定时",
    "manual": "手动",
    "limit": "水位"
}

# 间隔设置范围（分钟）
MIN_INTERVAL = 10
MAX_INTERVAL = 43200  # 30天