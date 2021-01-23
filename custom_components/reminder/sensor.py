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
    ATTR_HIDDEN,
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
    CONF_DATE_FORMAT,
    CONF_DESCRIPTION,
    CONF_EXCLUDE_DATES,
    CONF_ICON_ON,
    CONF_ICON_OFF,
    CONF_PERIOD,
    CONF_PERIOD_TEMPLATE,
    CONF_EXPIRE_AFTER,
    CONF_FIRST_DATE,
    CONF_FREQUENCY,
    CONF_INCLUDE_DATES,
    CONF_LAST_DATE,
    CONF_SUMMARY,
    CONF_TAG,
    CONF_START_TIME,
    CONF_END_TIME,
    CONF_TIME,
    CONF_TIME_FORMAT,
    CONF_VERBOSE_STATE,
    DEVICE_CLASS,
    DOMAIN,
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
        self._summary = self._name if config.get(CONF_SUMMARY) is None else config.get(CONF_SUMMARY)
        self._description = config.get(CONF_DESCRIPTION)
        self._next_date = None
        self._remaining = 0
        self._tag = config.get(CONF_TAG)
        self._period = config.get(CONF_PERIOD)
        self._period_template = config.get(CONF_PERIOD_TEMPLATE)
        self._verbose_state = config.get(CONF_VERBOSE_STATE)
        self._state = STATE_OFF
        self._icon = config.get(CONF_ICON)
        self._icon_on = config.get(CONF_ICON_ON)
        self._icon_off = config.get(CONF_ICON_OFF)
        self._frequency = config.get(CONF_FREQUENCY)
        self._date_format = config.get(CONF_DATE_FORMAT)
        self._date = self._to_date(config.get(CONF_DATE))
        self._time_format = config.get(CONF_TIME_FORMAT)
        self._time = self._to_time(config.get(CONF_TIME))
        self._start_time = self._to_time(config.get(CONF_START_TIME))
        self._end_time = self._to_time(config.get(CONF_END_TIME))
        self._last_date = self._to_date(config.get(CONF_LAST_DATE))
        self._first_date = self._to_date(config.get(CONF_FIRST_DATE))
        self._exclude_dates = self._to_dates(config.get(CONF_EXCLUDE_DATES, []))
        self._include_dates = self._to_dates(config.get(CONF_INCLUDE_DATES, []))
        exp = config.get(CONF_EXPIRE_AFTER)
        self.expire_after = (
            None if exp is None else datetime.strptime(exp, self._time_format).time()
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
        if self._icon_on and self._state == STATE_ON:
            return self._icon_on
        elif self._icon_off and self._state == STATE_OFF:
            return self._icon_off
        return self._icon

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        attribs = {}
        if self._next_date is None:
            attribs[ATTR_NEXT_DATE] = None
            attribs[ATTR_NEXT_TIME] = None
        else:
            attribs[ATTR_NEXT_DATE] = datetime(
                self._next_date.year, self._next_date.month, self._next_date.day,
                self._next_date.hour, self._next_date.minute
            ).astimezone()
        attribs[ATTR_REMAINING] = self._remaining
        attribs[ATTR_TAG] = self._tag
        return attribs

    @property
    def device_class(self):
        """Return the class of the sensor."""
        return DEVICE_CLASS

    @property
    def summary(self):
        """Return reminder summary."""
        return self._summary

    @property
    def description(self):
        """Return reminder description."""
        return self._description

    @property
    def start_time(self):
        """Return reminder start time."""
        if self._start_time:
            return self._start_time
        return self._to_time("00:00")

    @property
    def end_time(self):
        """Return reminder end time."""
        if self._end_time and self._end_time < self.start_time:
            return self.start_time + datetime.timedelta(hours=1)
        return self._end_time

    @property
    def all_day(self) -> bool:
        return self._start_time is None and self._end_time is None

    def _to_date(self, value: Any) -> str:
        """Convert str to dat."""
        if value is None or value == "":
            return None
        return datetime.strptime(value, self._date_format).date()

    def _to_dates(self, dates: List[Any]) -> List[date]:
        """Convert list of text to datetimes, if not already datetimes."""
        converted = []  # type: List[date]
        for day in dates:
            try:
                converted.append(self._to_date(day))
            except ValueError:
                continue
        return converted

    def _to_time(self, value: Any) -> str:
        """Convert str to time."""
        if value is None or value == "":
            return None
        return datetime.strptime(value, self._time_format).time()

    def _is_date_in_range(self, d: date) -> bool:
        """True if date is withing rreminder date range."""
        if not d:
            return False
        inside = True
        if self._first_date and d < self._first_date:
            inside = False
        if self._last_date and d > self._last_date:
            inside = False
        return inside

    def _is_time_in_range(self, t: datetime) -> bool:
        """True if given time is within reminder time range."""
        if not t:
            return True
        inside = True
        if self.start_time and t.time() < self.start_time:
            inside = False
        if self.end_time and t.time() > self.end_time:
            inside = False
        return inside

    def _next_date_none(self, first_date: date):
        """Returns single occurrence reminder next date (including reminder date)."""
        if self._date < first_date:
            return None
        return self._date

    def _next_date_daily(self, first_date: date):
        """Returns daily reminder next date occurrence (including reminder date)."""
        return first_date + relativedelta(days=(self._period - 1))
        
    def _next_date_weekly(self, first_date: date):
        """Returns weekly reminder next date occurrence."""
        next_date = first_date + relativedelta(days=(self._date.weekday() - first_date.weekday()))
        if next_date < first_date:
            next_date += relativedelta(days=(7 * self._period))
        return next_date

    def _next_date_monthly(self, first_date: date):
        """Returns monthly reminder next date occurrence (including reminder date)."""
        next_date = datetime(first_date.year, first_date.month, self._date.day)
        if next_date.date() < first_date:
            next_date += relativedelta(months=self._period)
        return next_date.date()

    def _next_date_yearly(self, first_date: date):
        """Returns yearly reminder next date occurrence (including reminder date)."""
        next_date = datetime(first_date.year, self._date.month, self._date.day)
        if next_date.date() < first_date:
            next_date += relativedelta(years=self._period)
        return next_date.date()

    def _find_next_date(self, first_date: date):
        """Returns reminder next date occurrence (including reminder date)."""
        if self._frequency == "none":
            return self._next_date_none(first_date)
        elif self._frequency == "daily":
            return self._next_date_daily(first_date)
        elif self._frequency == "weekly":
            return self._next_date_weekly(first_date)
        elif self._frequency == "monthly":
            return self._next_date_monthly(first_date)
        elif self._frequency == "yearly":
            return self._next_date_yearly(first_date)

    def _insert_include_date(self, first_date: date, next_date: Union[date, None]) -> Union[date, None]:
        """Add include dates."""
        include_dates = list(filter(lambda date: date >= first_date, self._include_dates))
        if len(include_dates) > 0 and (
            next_date is None or include_dates[0] < next_date
        ):
            _LOGGER.debug(
                "(%s) Inserting include_date %s", self._name, include_dates[0]
            )
            return include_dates[0]
        return next_date

    async def async_find_next_date(self, first_date: date, ignore_today=False):
        """Get date within configured date range."""
        day1 = first_date
        next_date = None
        while next_date is None:
            next_date = self._find_next_date(day1)
            # One time reminder
            if self._frequency == "none":
                break
            # Remove exclude dates
            if next_date in self._exclude_dates:
                _LOGGER.debug(
                    "(%s) Skipping exclude_date %s", self._name, next_date
                )
                next_date = None
            # Look from the next day
            day1 += relativedelta(days=1)
        if self._first_date and next_date < self._first_date:
            next_date = self._find_next_date(self._first_date)
        if self._last_date and next_date > self._last_date:
            next_date = None
        next_date = self._insert_include_date(first_date, next_date)
        return next_date

    async def async_update(self) -> None:
        """Get the latest data and updates the states."""
        now_date = datetime.now().date()
        next_date = self._find_next_date(now_date)
        if not next_date:
            return
        # Set attributes
        self._next_date = datetime.combine(next_date, self.start_time)
        self._remaining = (self._next_date.date() - now_date).days
        # Set state
        new_state = STATE_OFF
        reminder_date = await self.async_find_next_date(now_date)
        if reminder_date and (reminder_date == now_date):
            new_state = STATE_ON if self._is_time_in_range(datetime.now()) else STATE_OFF
        if new_state != self._state:
            self._state = new_state
