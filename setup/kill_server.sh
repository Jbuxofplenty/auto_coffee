#!/bin/bash
pid=$(sudo netstat -tupln | grep "8080" | awk '{print $7}' | awk -F/ '{print $1}' | head -1)
while [ ! -z "$pid" ]
do
sudo kill ${pid}
pid=$(sudo netstat -tupln | grep "8080" | awk '{print $7}' | awk -F/ '{print $1}' | head -1)
done