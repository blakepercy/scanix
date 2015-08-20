#!/bin/bash

set +e

SYSTEMS="etc/setalarm/systems.conf"

# kill the remote processes
sys=$(cat "$SYSTEMS" | sed -e :a -e '/./,$!d;/^\n*$/{$d;N;};/\n$/ba')

function rkill {
	echo Stopping $1 - $2 - $3
	sleep 1; sshpass -p "$2" ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no "$1" "kill -9 $3 &> /dev/null" &> /dev/null &
}

echo "$sys" |
(
	IFS=','
	while read name host port pass file; do
		echo $name, $host, $port, $pass, $file
		echo $(sleep 1; sshpass -p "$pass" ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -C "$host" -p "$port" "ps -ef | grep tail | grep while | tr -s ' ' | cut  -d ' ' -f 2") | { while read id; do rkill $host $pass $id; done } &
	done
)

# give the script time to establish the connection before exiting this script
sleep 15

# kill the local processes (may already be closed from the above closure)
pkill ssh
pkill cat
pkill tail
pkill flock
