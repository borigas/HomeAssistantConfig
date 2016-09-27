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
