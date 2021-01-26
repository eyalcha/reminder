"""Define constants used in reminder."""

# Base component constants
DOMAIN = "reminder"
DOMAIN_CONFIG = "config"
CALENDAR_NAME = "Reminders"
SENSOR_PLATFORM = "sensor"
CALENDAR_PLATFORM = "calendar"
ATTRIBUTION = "Data from this is provided by reminder."
ENTITY_ID_FORMAT = 'sensor' + '.{}'
ENTITY_ID_PREFIX_FORMAT = 'sensor' + '.{}_{}'

# Sensor attributes
ATTR_NEXT_DATE = "next_date"
ATTR_NEXT_DATE_VERBOSE = "next_date_verbose"
ATTR_DAYS = "days"
ATTR_REMAINING = "remaining"
ATTR_TAG = "tag"

# Device classes
BINARY_SENSOR_DEVICE_CLASS = "connectivity"
DEVICE_CLASS = "reminder__schedule"

# Configuration
CONF_CALENDAR = "calendar"
CONF_DATE = "date"
CONF_DATE_TEMPLATE = "date_template"
CONF_DATE_FORMAT = "date_format"
CONF_DESCRIPTION = "description"
CONF_ENABLED = "enabled"
CONF_PERIOD = "period"
CONF_PERIOD_TEMPLATE = "period_template"
CONF_EXCLUDE_DATES = "exclude_dates"
CONF_ICON_ON = "icon_on"
CONF_ICON_OFF = "icon_off"
CONF_INCLUDE_DATES = "include_dates"
CONF_FIRST_DATE = "first_date"
CONF_FREQUENCY = "frequency"
CONF_FREQUENCY_TEMPLATE = "frequency_template"
CONF_LAST_DATE = "last_date"
CONF_SENSORS = "sensors"
CONF_SUMMARY = "summary"
CONF_TAG = "tag"
CONF_TIME = "time"
CONF_START_TIME = "start_time"
CONF_END_TIME = "end_time"
CONF_TIME_FORMAT = "time_format"
CONF_VERBOSE_FORMAT = "verbose_format"
CONF_PREFIX = "prefix"

# Defaults
DEFAULT_CALENDAR = "Reminders"
DEFAULT_DATE_FORMAT = "%Y-%m-%d"
DEFAULT_ENABLED = True
DEFAULT_FREQUENCY = "none"
DEFAULT_ICON = 'mdi:calendar-blank'
DEFAULT_ICON_ON = 'mdi:calendar-star'
DEFAULT_ICON_OFF = 'mdi:calendar-blank'
DEFAULT_START_TIME = "00:00"
DEFAULT_TIME_FORMAT = "%H:%M"
DEFAULT_PERIOD = 1
DEFAULT_TAG = "reminder"
DEFAULT_VERBOSE_FORMAT = "Next on {date}"

#
FREQUENCY_OPTIONS = [
    "daily",
    "weekly",
    "monthly",
    "yearly",
    "none",
]

#
STATE_TYPE_OPTIONS = [
    "switch",
    "remaining"
]
