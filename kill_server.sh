#!/bin/bash
pid=$(ps -ef | awk '$8=="python3" {print $2}')
while [ ! -z "$pid" ]
do
kill ${pid}
pid=$(ps -ef | awk '$8=="python3" {print $2}')
done