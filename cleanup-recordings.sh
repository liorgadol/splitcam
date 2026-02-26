#!/bin/sh
# Cleanup script to delete recordings older than 1 day
# This script runs periodically to maintain only the last 24 hours of recordings

echo "$(date): Starting cleanup of recordings older than 1 day..."

# Delete camera1 recordings older than 1 day (1440 minutes)
find /recordings/camera1 -name "*.mp4" -type f -mmin +1440 -delete

# Delete camera2 recordings older than 1 day (1440 minutes)
find /recordings/camera2 -name "*.mp4" -type f -mmin +1440 -delete

echo "$(date): Cleanup completed"
