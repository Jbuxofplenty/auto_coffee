#!/bin/bash
scp ../auto_coffee.py pi@192.168.1.90:~
scp kill_server.sh pi@192.168.1.90:~
scp ../config.json pi@192.168.1.90:~
ssh pi@192.168.1.90 'sudo /home/pi/kill_server.sh && sudo python3 /home/pi/auto_coffee.py &'

# Only needs to run occasionally
# scp rc.local pi@192.168.1.90:~
# ssh pi@192.168.1.90 'sudo cp /home/pi/rc.local /etc/ && sudo chmod +x /etc/rc.local'
# ssh pi@192.168.1.90 'sudo reboot'
