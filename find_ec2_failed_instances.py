#!/usr/bin/env kpython
#
# print a list of 'failed' instances in ec2.
# first and only argument is the region to connect to (default: us-east-1)
# run from cron for each region to check.
#
import boto.ec2
import sys
import collections

regions = boto.ec2.regions()
names = [region.name for region in regions]

try:
    if len(sys.argv) > 1:
        region = regions[names.index(sys.argv[1])]
    else:
        region = regions[names.index('us-east-1')]
except ValueError:
    sys.stderr.write("Sorry, the region '%s' does not exist.\n" % sys.argv[1])
    sys.exit(1)  # proper return value for a script run as a command

ec2 = region.connect()
stats = ec2.get_all_instance_status(filters={"system-status.reachability": "failed"})

if len(stats) > 0:
    print "The following instances show 'failed' for the ec2 reachability check: "

for stat in stats:
    reservation = ec2.get_all_instances(filters={'instance-id': stat.id})
    dead_instance = reservation[0].instances[0]

    print dead_instance.tags.get('Name'), stat.id, stat.zone, stat.state_name

    if isinstance(stat.events, collections.Iterable):
        print "\tmost recent events: ", [(event.code, event.description) for event in stat.events]
