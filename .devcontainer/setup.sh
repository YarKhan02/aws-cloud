#!/bin/bash

# Set the IP_GITHUB environment variable
export IP_GITHUB=$(curl -s ifconfig.me)
echo "IP_GITHUB=$IP_GITHUB" >> /etc/environment

# Run the rds-update-sg-rule script
bash $THEIA_WORKSPACE_ROOT/backend-flask/bin/rds-update-sg-rule
