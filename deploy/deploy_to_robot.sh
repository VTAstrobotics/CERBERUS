#!/bin/bash

# This script copies your entire CERBERUS directory to a remote robot
# over SSH using rsync. It assumes you have SSH access to the robot.
# This means that you do not need to connect the robot to the internet or to a monitor 
# unless you are adding external dependencies. The syncing should handle any amount of changes you may be making
# note that the CERBERUS directory on the robot will be replaced with your local copy.
# and the CERBERUS Directory on the robot will be located at ~/Deployments/CERBERUS
# The normal CERBERUS directory will be left alone for any potential edge cases.

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
CERBERUS_DIR="$( dirname "$SCRIPT_DIR" )"   # parent of deploy

Dest_IP="$1"

if [ -z "$Dest_IP" ]; then
  echo "Usage: $0 user@host:/path"
  echo
  echo "Description:"
  echo "  user@host:/path  The SSH destination where the CERBERUS directory"
  echo "                   will be synced. Example:"
  echo "                   ./sync.sh rover@192.168.1.50"
  exit 1
fi



Dest="$Dest_IP":/home/astrobotics/Deployments/CERBERUS

ssh "$Dest_IP" "mkdir -p /home/astrobotics/Deployments/CERBERUS"

rsync -avz --delete --exclude "build/" --exclude "log/" --exclude "install/" "$CERBERUS_DIR/" "$Dest/"