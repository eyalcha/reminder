"""Sensor platform for reminders."""

import asyncio
import logging

from typing import Any, List, Optional, Union

from datetime import date, datetime, time, timedelta

from dateutil.parser import parse
from dateutil.relativedelta import relativedelta

from homeassistant.components.template.template_entity import TemplateEntity

from homeassistant.helpers.discovery import async_load_platform
from homeassistant.helpers.restore_state import RestoreEntity

from homeassistant.const import (
    ATTR_HIDDEN, ATTR_FRIENDLY_NAME,
    CONF_ENTITIES, CONF_NAME, CONF_ICON,
    WEEKDAYS,
    STATE_ON,
    STATE_OFF
)

from .calendar import EntitiesCalendarData

from .const import (
    ATTR_NEXT_DATE,
    ATTR_REMAINING,
    ATTR_TAG,
    CALENDAR_NAME,
    CALENDAR_PLATFORM,
    CONF_DATE,
    CONF_PERIOD,
    CONF_PERIOD_TEMPLATE,
    CONF_EXPIRE_AFTER,
    CONF_FIRST_DATE,
    CONF_FREQUENCY,
    CONF_LAST_DATE,
    CONF_TAG,
    CONF_TIME,
    CONF_VERBOSE_STATE,
    DEVICE_CLASS,
    DOMAIN,
    EVENT_REMINDER,
    SENSOR_PLATFORM,
)

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=60)


async def async_setup_platform(hass, _, async_add_entities, discovery_info=None):
    """Create reminders entities defined in YAML and add them to HA."""
    async_add_entities([ReminderSensor(hass, discovery_info)], True)


class ReminderSensor(TemplateEntity, RestoreEntity):
    """Reminder Sensor class."""

    def __init__(self, hass, config, title=None):
        """Initialize the Template Media player."""
        super().__init__(
        )
        self._config = config
        self._hass = hass
        self._hidden = config.get(ATTR_HIDDEN, False)
        self._name = config.get(CONF_NAME)
        self._friendly_name = config.get(ATTR_FRIENDLY_NAME)
        self._next_date = None
        self._remaining = 0
        self._tag = config.get(CONF_TAG)
        self._period = config.get(CONF_PERIOD)
        self._period_template = config.get(CONF_PERIOD_TEMPLATE)
        self._verbose_state = config.get(CONF_VERBOSE_STATE)
        self._state = STATE_OFF
        self._icon = config.get(CONF_ICON)
        self._frequency = config.get(CONF_FREQUENCY)
        self._date = self.to_date(config.get(CONF_DATE))
        self._time = self.to_time(config.get(CONF_TIME))
        self._last_date = self.to_date(config.get(CONF_LAST_DATE))
        self._first_date = self.to_date(config.get(CONF_FIRST_DATE))
        exp = config.get(CONF_EXPIRE_AFTER)
        self.expire_after = (
            None if exp is None else datetime.strptime(exp, "%H:%M").time()
        )

    async def async_added_to_hass(self):
        """When sensor is added to hassio, add it to calendar."""
        await super().async_added_to_hass()
        if DOMAIN not in self.hass.data:
            self.hass.data[DOMAIN] = {}
        if SENSOR_PLATFORM not in self.hass.data[DOMAIN]:
            self.hass.data[DOMAIN][SENSOR_PLATFORM] = {}
        self.hass.data[DOMAIN][SENSOR_PLATFORM][self.entity_id] = self

        state = await self.async_get_last_state()

        if self._period_template is not None:
            self.add_template_attribute("_period", self._period_template)

        if not self.hidden:
            if CALENDAR_PLATFORM not in self.hass.data[DOMAIN]:
                self.hass.data[DOMAIN][CALENDAR_PLATFORM] = EntitiesCalendarData(
                    self.hass
                )
                _LOGGER.debug("Creating reminders calendar")
                self.hass.async_create_task(
                    async_load_platform(
                        self.hass,
                        CALENDAR_PLATFORM,
                        DOMAIN,
                        {"name": CALENDAR_NAME},
                        {"name": CALENDAR_NAME},
                    )
                )
            _LOGGER.debug(f"Add entity {self.entity_id}")
            self.hass.data[DOMAIN][CALENDAR_PLATFORM].add_entity(self.entity_id)

    @property
    def unique_id(self):
        """Return a unique ID to use for this sensor."""
        return self._config.get("unique_id", None)

    @property
    def device_info(self):
        """Return device info."""
        return {
            "identifiers": {(DOMAIN, self._config.get("unique_id", None))},
            "name": self._config.get("name"),
            "manufacturer": "Reminders",
        }

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def hidden(self):
        """Return the hidden attribute."""
        return self._hidden

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state

    @property
    def icon(self):
        """Return the entity icon."""
        return self._icon

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        attribs = {}
        if self._next_date is None:
            attribs[ATTR_NEXT_DATE] = None
        else:
            attribs[ATTR_NEXT_DATE] = datetime(
                self._next_date.year, self._next_date.month, self._next_date.day
            ).astimezone()
        attribs[ATTR_REMAINING] = self._remaining
        attribs[ATTR_TAG] = self._tag
        return attribs

    @property
    def device_class(self):
        """Return the class of the sensor."""
        return DEVICE_CLASS

    def to_date(self, value: Any) -> str:
        """Convert str to dat."""
        if value is None or value == "":
            return None
        return datetime.strptime(value, "%Y-%m-%d").date()

    def to_time(self, value: Any) -> str:
        """Convert str to time."""
        if value is None or value == "":
            return None
        return datetime.strptime(value, "%H:%M").time()

    def is_date_in_range(self, d: date) -> bool:
        """True if date is withing rreminder date range."""
        if not d:
            return False
        inside = True
        if self._first_date and d < self._first_date:
            inside = False
        if self._last_date and d > self._last_date:
            inside = False
        return inside

    def is_time_in_range(self, t: datetime) -> bool:
        """True if given time is within reminder time range."""
        if not t:
            return True
        inside = False
        if self._time and t.time() > self._time:
            inside = True
        return inside

    def next_date_none(self, first_date: date):
        """Returns single occurrence reminder next date (including reminder date)."""
        if self._date < first_date:
            return None
        return self._date

    def next_date_daily(self, first_date: date):
        """Returns daily reminder next date occurrence (including reminder date)."""
        return first_date + relativedelta(days=(self._period - 1))
        
    def next_date_weekly(self, first_date: date):
        """Returns weekly reminder next date occurrence."""
        next_date = first_date + relativedelta(days=(self._date.weekday() - first_date.weekday()))
        if next_date < first_date:
            next_date += relativedelta(days=(7 * self._period))
        return next_date

    def next_date_monthly(self, first_date: date):
        """Returns monthly reminder next date occurrence (including reminder date)."""
        next_date = datetime(first_date.year, first_date.month, self._date.day)
        if next_date.date() < first_date:
            next_date += relativedelta(months=self._period)
        return next_date.date()

    def next_date_yearly(self, first_date: date):
        """Returns yearly reminder next date occurrence (including reminder date)."""
        next_date = datetime(first_date.year, self._date.month, self._date.day)
        if next_date.date() < first_date:
            next_date += relativedelta(years=self._period)
        return next_date.date()

    def next_date(self, first_date: date):
        """Returns reminder next date occurrence (including reminder date)."""
        if self._frequency == "none":
            return  self.next_date_none(first_date)
        elif self._frequency == "daily":
            return self.next_date_daily(first_date)
        elif self._frequency == "weekly":
            return self.next_date_weekly(first_date)
        elif self._frequency == "monthly":
            return self.next_date_monthly(first_date)
        elif self._frequency == "yearly":
            return self.next_date_yearly(first_date)

    async def async_find_next_date(self, first_date: date, ignore_today=False):
        """Get date within configured date range."""
        next_date = self.next_date(first_date)
        if self._first_date and next_date < self._first_date:
            next_date = self.next_date(self._first_date)
        if self._last_date and next_date > self._last_date:
            next_date = None
        return next_date

    def fire_reminder_state(self):
        self._hass.bus.fire(EVENT_REMINDER, {
            "entity_id": self.unique_id, "state": self._state
        })

    async def async_update(self) -> None:
        """Get the latest data and updates the states."""
        now_date = datetime.now().date()
        next_date = self.next_date(now_date)
        if not next_date:
            return
        # Set attributes
        self._next_date = datetime.combine(next_date, self._time)
        self._remaining = (self._next_date.date() - now_date).days
        # Set state
        new_state = STATE_OFF
        reminder_date = self.next_date(now_date)
        if reminder_date and (reminder_date == now_date):
            new_state = STATE_ON if self.is_time_in_range(datetime.now()) else STATE_OFF
        if new_state != self._state:
            self._state = new_state
            self.fire_reminder_state()

