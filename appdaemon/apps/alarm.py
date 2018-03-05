import appdaemon.plugins.hass.hassapi as hass

#
# Hellow World App
#
# Args:
#

class Alarm(hass.Hass):

  def initialize(self):
     self.log("Hello from AppDaemon Alarm")
     self.log("You are now ready to run Apps!")
