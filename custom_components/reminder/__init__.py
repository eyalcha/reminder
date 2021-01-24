"""Component to integrate with reminder."""

from datetime import timedelta
import logging

import homeassistant.helpers.config_validation as cv
import homeassistant.util.dt as dt_util

from homeassistant import config_entries
from homeassistant.const import ATTR_HIDDEN, ATTR_FRIENDLY_NAME, CONF_NAME, CONF_ICON

from homeassistant.helpers import discovery

import voluptuous as vol

from .const import (
    CONF_CALENDAR,
    CONF_DATE,
    CONF_DATE_TEMPLATE,
    CONF_DATE_FORMAT,
    CONF_DESCRIPTION,
    CONF_ENABLED,
    CONF_EXCLUDE_DATES,
    CONF_FIRST_DATE,
    CONF_FREQUENCY,
    CONF_FREQUENCY_TEMPLATE,
    CONF_ICON_OFF,
    CONF_ICON_ON,
    CONF_INCLUDE_DATES,
    CONF_LAST_DATE,
    CONF_PERIOD,
    CONF_PERIOD_TEMPLATE,
    CONF_PREFIX,
    CONF_SENSORS,
    CONF_SUMMARY,
    CONF_TAG,
    CONF_TIME,
    CONF_START_TIME,
    CONF_END_TIME,
    CONF_TIME_FORMAT,
    DEFAULT_CALENDAR,
    DEFAULT_DATE_FORMAT,
    DEFAULT_ENABLED,
    DEFAULT_FREQUENCY,
    DEFAULT_ICON,
    DEFAULT_ICON_OFF,
    DEFAULT_ICON_ON,
    DEFAULT_PERIOD,
    DEFAULT_TAG,
    DEFAULT_TIME_FORMAT,
    DOMAIN,
    DOMAIN_CONFIG,
    FREQUENCY_OPTIONS,
    SENSOR_PLATFORM,
)

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=30)

_LOGGER = logging.getLogger(__name__)

SENSOR_CONFIG_SCHEMA = vol.Schema({
    vol.Required(CONF_NAME): cv.string,
    vol.Optional(ATTR_FRIENDLY_NAME): cv.string,
    vol.Optional(CONF_CALENDAR, default=DEFAULT_CALENDAR): cv.string,
    vol.Optional(CONF_DATE): cv.string,
    vol.Optional(CONF_DATE_TEMPLATE): cv.template,
    vol.Optional(CONF_DATE_FORMAT, default=DEFAULT_DATE_FORMAT): cv.string,
    vol.Optional(CONF_ICON, default=DEFAULT_ICON): cv.string,
    vol.Optional(CONF_ICON_ON, default=DEFAULT_ICON_ON): cv.string,
    vol.Optional(CONF_ICON_OFF, default=DEFAULT_ICON_OFF): cv.string,
    vol.Optional(CONF_FREQUENCY, default=DEFAULT_FREQUENCY): vol.In(FREQUENCY_OPTIONS),
    vol.Optional(CONF_FREQUENCY_TEMPLATE): cv.template,
    vol.Optional(CONF_TIME): cv.string,
    vol.Optional(CONF_START_TIME): cv.string,
    vol.Optional(CONF_END_TIME): cv.string,
    vol.Optional(CONF_TIME_FORMAT, default=DEFAULT_TIME_FORMAT): cv.string,
    vol.Optional(CONF_FIRST_DATE): cv.string,
    vol.Optional(CONF_LAST_DATE): cv.string,
    vol.Optional(CONF_PERIOD, default=DEFAULT_PERIOD): cv.positive_int,
    vol.Optional(CONF_PERIOD_TEMPLATE): cv.template,
    vol.Optional(ATTR_HIDDEN, default=False): cv.boolean,
    vol.Optional(CONF_TAG, default=DEFAULT_TAG): cv.string,
    vol.Optional(CONF_SUMMARY): cv.string,
    vol.Optional(CONF_DESCRIPTION): cv.string,
    vol.Optional(CONF_EXCLUDE_DATES): cv.ensure_list,
    vol.Optional(CONF_INCLUDE_DATES): cv.ensure_list,
    vol.Optional(CONF_ENABLED, default=DEFAULT_ENABLED): cv.boolean,
})

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: {
        vol.Optional(CONF_SENSORS): vol.All(cv.ensure_list, [SENSOR_CONFIG_SCHEMA]),
        vol.Optional(CONF_PREFIX): cv.string,
    }
}, extra=vol.ALLOW_EXTRA)


async def async_setup(hass, config):
    """Set up this component using YAML."""

    if config.get(DOMAIN) is None:
        # We get here if the integration is set up using config flow
        return True

    platform_config = config[DOMAIN].get(CONF_SENSORS)
    # If platform is not enabled, skip.
    if not platform_config:
        return False

    # Platform global configurations
    hass.data[DOMAIN] = {}
    hass.data[DOMAIN][DOMAIN_CONFIG] = config[DOMAIN]

    for entry in platform_config:
        _LOGGER.debug(
            "Setting %s from YAML configuration",
            entry[CONF_NAME],
        )
        # If entry is not enabled, skip.
        if not entry[CONF_ENABLED]:
            continue
        hass.async_create_task(
            discovery.async_load_platform(hass, SENSOR_PLATFORM, DOMAIN, entry, config)
        )
    
    return True
