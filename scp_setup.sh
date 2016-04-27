#!/usr/bin/env bash

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

ssh-keygen -t rsa -b 2048 -C "bob" -f bob_key -N ''

mkdir -p /home/bob/.ssh
cp bob_key.pub /home/bob/.ssh/authorized_keys
chown -R bob:bob /home/bob/.ssh
chmod 0700 /home/bob/.ssh
chmod 0600 /home/bob/.ssh/authorized_keys

echo "private key for sending builds:"
cat bob_key

# TODO add a better explanation of what to do here
