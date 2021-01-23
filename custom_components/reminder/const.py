"""Define constants used in reminder."""

# Base component constants
DOMAIN = "reminder"
CALENDAR_NAME = "Reminders"
SENSOR_PLATFORM = "sensor"
CALENDAR_PLATFORM = "calendar"
ATTRIBUTION = "Data from this is provided by reminder."

#
ATTR_NEXT_DATE = "next_date"
ATTR_DAYS = "days"
ATTR_REMAINING = "remaining"
ATTR_TAG = "tag"

# Device classes
BINARY_SENSOR_DEVICE_CLASS = "connectivity"
DEVICE_CLASS = "reminder__schedule"

# Configuration
CONF_EXPIRE_AFTER = "expire_after"
CONF_DATE = "date"
CONF_DATE_FORMAT = "date_format"
CONF_DESCRIPTION = "description"
CONF_PERIOD = "period"
CONF_PERIOD_TEMPLATE = "period_template"
CONF_EXCLUDE_DATES = "exclude_dates"
CONF_INCLUDE_DATES = "include_dates"
CONF_FIRST_DATE = "first_date"
CONF_FREQUENCY = "frequency"
CONF_LAST_DATE = "last_date"
CONF_SENSORS = "sensors"
CONF_STATE_TYPE = "state_type"
CONF_SUMMARY = "summary"
CONF_TAG = "tag"
CONF_TIME = "time"
CONF_TIME_FORMAT = "time_format"
CONF_VERBOSE_STATE = "verbose_state"

# Defaults
DEFAULT_DATE_FORMAT = "%Y-%m-%d"
DEFAULT_FREQUENCY = "none"
DEFAULT_ICON = 'mdi:calendar-star'
DEFAULT_TIME = "00:00"
DEFAULT_TIME_FORMAT = "%H:%M"
DEFAULT_PERIOD = 1
DEFAULT_TAG = "reminder"

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
