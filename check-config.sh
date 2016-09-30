#!/bin/bash

# Become user 'hass'
sudo su -s /bin/bash hass <<'EOF'
# Activate the virtualenv
source /srv/hass/hass_venv/bin/activate

hass --script check_config -c /home/pi/HomeAssistantConfig
exit
EOF
