import appdaemon.plugins.hass.hassapi as hass
import datetime

class Alarm(hass.Hass):
  HOUR_ENTITY = "input_number.alarm_hour"
  MINUTE_ENTITY = "input_number.alarm_minute"
  ALARM_ENTITY = "group.bedroom_alarm_lights"
  DAY_TOGGLE = "input_boolean.alarm_lights_today"
  FUTURE_TOGGLE = "input_boolean.alarm_lights"

  ALARM_ACTIVE_SECONDS = 60 * 30
  ALARM_COMPLETE_SECONDS = 60 * 60

  ALARM_END_BRIGHTNESS = 200

  def initialize(self):
    self.log("Initializing AppDaemon Alarm")

    self.timeListener = None
    self.brightness = 0

    self.setupConfigChangeListeners()
    self.reinitTimeListener()

    self.log("Alarm initialized")
  
  def setupConfigChangeListeners(self):
    self.listen_state(self.sliderChanged, Alarm.HOUR_ENTITY)
    self.listen_state(self.sliderChanged, Alarm.MINUTE_ENTITY)

  def sliderChanged(self, entity, attribute, old, new, kwargs):
    self.reinitTimeListener()

  def reinitTimeListener(self):
    if(self.timeListener != None):
      self.cancel_timer(self.timeListener)

    hour = self.getStateAsInt(Alarm.HOUR_ENTITY)
    minute = self.getStateAsInt(Alarm.MINUTE_ENTITY)
    time = datetime.time(hour, minute, 0)
    self.timeListener = self.run_daily(self.startAlarmTimerCallback, time)
    self.log(f"Created listener for {time}")

  def getStateAsInt(self, entity):
    rawState = self.get_state(entity)
    floatState = float(rawState)
    intState = int(floatState)
    return intState

  def getStateAsBool(self, entity):
    rawState = self.get_state(entity)
    isOn = rawState == "on"
    return isOn

  def getIsAlarmEnabled(self):
    isEnabled = self.getStateAsBool(Alarm.DAY_TOGGLE)
    return isEnabled

  def startAlarmTimerCallback(self, kwargs):
    self.log("Timer callback triggered")

    if(self.getIsAlarmEnabled()):
      self.log("Alarms enabled. Starting")
      resetIn = 60 * 60
      self.run_in(self.resetAlarmTimerCallback, Alarm.ALARM_COMPLETE_SECONDS)

      self.brightness = 0
      self.increaseBrightness()
      self.startBrightnessTimer()

    self.log("Timer callback finished")

  def startBrightnessTimer(self):
    updateInterval = Alarm.ALARM_ACTIVE_SECONDS / Alarm.ALARM_END_BRIGHTNESS
    self.run_in(self.updateBrightnessCallback, updateInterval)

  def updateBrightnessCallback(self, kwargs):
    if(self.getIsAlarmEnabled() and self.brightness <= Alarm.ALARM_END_BRIGHTNESS):
      self.increaseBrightness()
      self.startBrightnessTimer()

  def increaseBrightness(self):
    self.brightness += 1
    self.log(f"Setting {Alarm.ALARM_ENTITY} to {self.brightness}")
    self.turn_on(Alarm.ALARM_ENTITY, brightness=self.brightness)

  def resetAlarmTimerCallback(self, kwargs):
    self.log("Resetting alarm")

    if(self.getIsAlarmEnabled()):
      self.turn_off(Alarm.ALARM_ENTITY)

    futureAlarmState = self.get_state(Alarm.FUTURE_TOGGLE)
    self.set_state(Alarm.DAY_TOGGLE, state = futureAlarmState)
    self.log(f"Alarm reset to {futureAlarmState} and {Alarm.ALARM_ENTITY} set to off")



