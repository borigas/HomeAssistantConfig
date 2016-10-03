#!/bin/bash

# Stop HASS
#sudo systemctl stop home-assistant.service
# Become user 'hass'
sudo su -s /bin/bash hass <<'EOF'
# Activate the virtualenv
source /srv/hass/hass_venv/bin/activate
# Install Home Assistant
pip3 install --upgrade homeassistant
exit
EOF

# Restart Home Assistant
sudo systemctl restart home-assistant.service

# Push updated HA_VERSION to github
git -C "/home/pi/HomeAssistantConfig" add "/home/pi/HomeAssistant/.HA_VERSION"
git -C "/home/pi/HomeAssistantConfig" commit -m "Updated to new version"
git -C "/home/pi/HomeAssistantConfig" push

