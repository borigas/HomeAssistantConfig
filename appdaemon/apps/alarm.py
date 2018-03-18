import appdaemon.plugins.hass.hassapi as hass
import datetime

class Alarm(hass.Hass):
  HOUR_ENTITY = "input_number.alarm_hour"
  MINUTE_ENTITY = "input_number.alarm_minute"
  ALARM_ENTITY = "group.bedroom_alarm_lights"
  #ALARM_ENTITY = "switch.kitchen_ceiling_switch"

  MUSIC_SOURCE = "Bedroom Echo Dot"
  #MUSIC_SOURCE = "Living Room Echo Dot"

  SPOTIFY_ENTITY = "media_player.spotify"

  DAY_TOGGLE = "input_boolean.alarm_lights_today"
  FUTURE_TOGGLE = "input_boolean.alarm_lights"

  ALARM_ACTIVE_SECONDS = 60 * 30
  ALARM_COMPLETE_SECONDS = 60 * 60

  ALARM_END_BRIGHTNESS = 200
  END_VOLUME = 0.6
  VOLUME_STEP = 0.05

  DEBUG = False

  PLAYLIST = "spotify:user:spotify:playlist:37i9dQZEVXcN0w5MZ6mb7Y"

  def initialize(self):
    self.log("Initializing AppDaemon Alarm")

    self.isAlarmFinished = False
    self.timeListener = None
    self.brightness = 0
    self.volume = 0

    if(Alarm.DEBUG):
      time = datetime.datetime.now()
      self.set_state(Alarm.HOUR_ENTITY, state = time.hour)
      self.set_state(Alarm.MINUTE_ENTITY, state = time.minute + 1)

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
    # Weekday is 0-6 starting on Mon
    isWeekday = datetime.today().weekday() <= 4
    isEnabled = isWeekday and self.getStateAsBool(Alarm.DAY_TOGGLE) and not self.isAlarmFinished
    return isEnabled

  def startAlarmTimerCallback(self, kwargs):
    self.log("Timer callback triggered")
    self.isAlarmFinished = False

    if(self.getIsAlarmEnabled()):
      self.log("Alarms enabled. Starting")
      resetIn = 60 * 60
      self.run_in(self.resetAlarmTimerCallback, Alarm.ALARM_COMPLETE_SECONDS)

      self.brightness = 0
      self.increaseBrightnessAndStartTimer()

      self.startMusic()

    self.log("Timer callback finished")

  ### Lights
  def increaseBrightnessAndStartTimer(self):
    if(self.getIsAlarmEnabled() and self.brightness <= Alarm.ALARM_END_BRIGHTNESS):
      self.increaseBrightness()
      self.startBrightnessTimer()

  def increaseBrightness(self):
    self.brightness += 1
    self.log(f"Setting {Alarm.ALARM_ENTITY} to {self.brightness}")
    self.turn_on(Alarm.ALARM_ENTITY, brightness=self.brightness)

  def startBrightnessTimer(self):
    updateInterval = Alarm.ALARM_ACTIVE_SECONDS / Alarm.ALARM_END_BRIGHTNESS
    self.run_in(self.updateBrightnessCallback, updateInterval)

  def updateBrightnessCallback(self, kwargs):
    self.increaseBrightnessAndStartTimer()

  ### Music
  def startMusic(self):
    self.call_service("media_player/media_pause", entity_id = Alarm.SPOTIFY_ENTITY)
    self.log(f"Setting {Alarm.SPOTIFY_ENTITY} source to {Alarm.MUSIC_SOURCE}")
    self.call_service("media_player/select_source", entity_id = Alarm.SPOTIFY_ENTITY, source = Alarm.MUSIC_SOURCE)
    self.volume = 0
    self.updateVolume()
    # Give volume a chance to sync before starting to avoid loud initial volume
    self.run_in(self.startPlaylist, 10)

  def startPlaylist(self, kwargs):
    self.log(f"Starting playlist")
    self.call_service("media_player/play_media", entity_id = Alarm.SPOTIFY_ENTITY, media_content_id = Alarm.PLAYLIST, media_content_type = "playlist")
    self.increaseVolumeAndStartTimer()

  def increaseVolumeAndStartTimer(self):
    if(self.getIsAlarmEnabled() and self.volume < Alarm.END_VOLUME):
      self.volume += Alarm.VOLUME_STEP
      self.updateVolume()
      self.startVolumeTimer()

  def updateVolume(self):
    self.log(f"Setting volume to {self.volume}")
    self.call_service("media_player/volume_set", entity_id = Alarm.SPOTIFY_ENTITY, volume_level = self.volume)

  def startVolumeTimer(self):
    updateInterval = Alarm.ALARM_ACTIVE_SECONDS / (Alarm.END_VOLUME / Alarm.VOLUME_STEP)
    self.run_in(self.updateVolumeCallback, updateInterval)

  def updateVolumeCallback(self, kwargs):
    self.increaseVolumeAndStartTimer()


  def resetAlarmTimerCallback(self, kwargs):
    self.log("Resetting alarm")
    self.isAlarmFinished = True

    if(self.getIsAlarmEnabled()):
      self.turn_off(Alarm.ALARM_ENTITY)

    currentSource = self.get_state(Alarm.SPOTIFY_ENTITY, attribute = "source")
    if(currentSource == Alarm.MUSIC_SOURCE):
      self.call_service("media_player/media_pause", entity_id = Alarm.SPOTIFY_ENTITY)

    futureAlarmState = self.get_state(Alarm.FUTURE_TOGGLE)
    self.set_state(Alarm.DAY_TOGGLE, state = futureAlarmState)
    self.log(f"Alarm reset to {futureAlarmState} and {Alarm.ALARM_ENTITY} set to off")