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
    CONF_DATE,
    CONF_FIRST_DATE,
    CONF_FREQUENCY,
    CONF_LAST_DATE,
    CONF_PERIOD,
    CONF_PERIOD_TEMPLATE,
    CONF_SENSORS,
    CONF_STATE_TYPE,
    CONF_TAG,
    CONF_TIME,
    DEFAULT_FREQUENCY,
    DEFAULT_ICON,
    DEFAULT_PERIOD,
    DEFAULT_TAG,
    DEFAULT_TIME,
    DOMAIN,
    FREQUENCY_OPTIONS,
    SENSOR_PLATFORM,
)

MIN_TIME_BETWEEN_UPDATES = timedelta(seconds=30)

_LOGGER = logging.getLogger(__name__)

SENSOR_CONFIG_SCHEMA = vol.Schema({
    vol.Required(CONF_NAME): cv.string,
    vol.Optional(ATTR_FRIENDLY_NAME): cv.string,
    vol.Required(CONF_DATE): cv.string,
    vol.Optional(CONF_ICON, default=DEFAULT_ICON): cv.string,
    vol.Optional(CONF_FREQUENCY, default=DEFAULT_FREQUENCY): vol.In(FREQUENCY_OPTIONS),
    vol.Optional(CONF_TIME, default=DEFAULT_TIME): cv.string,
    vol.Optional(CONF_FIRST_DATE): cv.string,
    vol.Optional(CONF_LAST_DATE): cv.string,
    vol.Optional(CONF_PERIOD, default=DEFAULT_PERIOD): cv.positive_int,
    vol.Optional(CONF_PERIOD_TEMPLATE): cv.template,
    vol.Optional(ATTR_HIDDEN, default=False): cv.boolean,
    vol.Optional(CONF_TAG, default=DEFAULT_TAG): cv.string,
})

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: {vol.Optional(CONF_SENSORS): vol.All(cv.ensure_list, [SENSOR_CONFIG_SCHEMA])}
}, extra=vol.ALLOW_EXTRA)


async def async_setup(hass, config):
    """Set up this component using YAML."""

    # def handle_collect_garbage(call):
    #     """Handle the service call."""
    #     entity_id = call.data.get(CONF_ENTITY_ID)
    #     last_collection = call.data.get(ATTR_LAST_COLLECTION)
    #     _LOGGER.debug("called collect_garbage for %s", entity_id)
    #     try:
    #         entity = hass.data[DOMAIN][SENSOR_PLATFORM][entity_id]
    #         if last_collection is None:
    #             entity.last_collection = dt_util.now()
    #         else:
    #             entity.last_collection = dt_util.as_local(last_collection)
    #     except Exception as err:
    #         _LOGGER.error("Failed setting last collection for %s - %s", entity_id, err)
    #     hass.services.call("homeassistant", "update_entity", {"entity_id": entity_id})

    # if DOMAIN not in hass.services.async_services():
    #     hass.services.async_register(
    #         DOMAIN, "collect_garbage", handle_collect_garbage, schema=COLLECT_NOW_SCHEMA
    #     )
    # else:
    #     _LOGGER.debug("Service already registered")

    if config.get(DOMAIN) is None:
        # We get here if the integration is set up using config flow
        return True

    platform_config = config[DOMAIN].get(CONF_SENSORS)
    # If platform is not enabled, skip.
    if not platform_config:
        return False

    for entry in platform_config:
        _LOGGER.debug(
            "Setting %s from YAML configuration",
            entry[CONF_NAME],
        )
        # If entry is not enabled, skip.
        # if not entry[CONF_ENABLED]:
        #     continue
        hass.async_create_task(
            discovery.async_load_platform(hass, SENSOR_PLATFORM, DOMAIN, entry, config)
        )
    
    return True
