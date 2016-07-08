import logging
import homeassistant.helpers.entity import ToggleEntity


DOMAIN = 'alarm_clock'

ENTITY_ID_FORMAT = DOMAIN + '.{}'

def setup_platform(hass, config, add_devices, discovery_info=None):
#	hass.states.set(

	clock = AlarmClock('bedroom', 'Bedroom Alarm', 'mdi:hotel')

	add_devices([clock])



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
