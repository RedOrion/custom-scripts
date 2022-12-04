#!/bin/python3

import psutil

partitions = psutil.disk_partitions()

for partition in partitions:
    usage = psutil.disk_usage(partition.mountpoint)
    if usage.percent > 50:
        if("snap" not in partition.mountpoint): {
            print(f"{partition.mountpoint} is using {usage.percent}% of its total space.")
        }
