#!/bin/sh

PATH="/home/forcer/Projects/eveutil/2.0/scripts:$PATH"
grdassetsdump > /home/forcer/Depot/EVE/grdassets/$(date +"%Y-%m-%d.csv")
