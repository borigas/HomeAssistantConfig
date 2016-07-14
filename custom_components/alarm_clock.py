import logging
from homeassistant.helpers.entity import ToggleEntity
from homeassistant.helpers.entity_component import EntityComponent
from homeassistant.const import (ATTR_ENTITY_ID, SERVICE_TURN_OFF, SERVICE_TURN_ON, STATE_ON)

DOMAIN = 'alarm_clock'

ENTITY_ID_FORMAT = DOMAIN + '.{}'

_LOGGER = logging.getLogger(__name__)

def is_on(hass, entity_id):
	return hass.states.is_state(entity_id, STATE_ON)

def turn_on(hass, entity_id):
	hass.services.call(DOMAIN, SERVICE_TURN_ON, {ATTR_ENTITY_ID: entity_id})

def turn_off(hass, entity_id):
	hass.services.call(DOMAIN, SERVICE_TURN_OFF, {ATTR_ENTITY_ID: entity_id})


def setup(hass, config):
	_LOGGER.info('Setting up ' + DOMAIN)

	def toggle_service(service):
		target_inputs = component.extract_from_service(service)
		
		for input_b in target_inputs:
			if service.service == SERVICE_TURN_ON:
				input_b.turn_on()
			else:
				input_b.turn_off()

	hass.services.register(DOMAIN, SERVICE_TURN_OFF, toggle_service)
	hass.services.register(DOMAIN, SERVICE_TURN_ON, toggle_service)
	

	component = EntityComponent(_LOGGER, DOMAIN, hass)

	clock = AlarmClock('bedroom', 'Bedroom Alarm', 'mdi:hotel')

	_LOGGER.info('Created ' + DOMAIN + ' instance')

	component.add_entities([clock])

	_LOGGER.info('Added ' + DOMAIN + ' devices')
	
	return True


class AlarmClock(ToggleEntity):
	

	def __init__(self, object_id, name, icon):
		self.entity_id = ENTITY_ID_FORMAT.format(object_id)
		self._name = name
		self._icon = icon
		self._state = True
		
	@property
	def name(self):
		return self._name

	@property
	def icon(self):
		return self._icon

	@property
	def is_on(self):
		return self._state

	@property
	def should_poll(self):
		return False

	def turn_on(self, **kwargs):
		self._state = True
		self.update_ha_state()

	def turn_off(self, **kwargs):
		self._state = False
		self.update_ha_state()
