#!/usr/bin/env bash

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

if [ -z "$1" ]
  then
    echo "This script requires your domain as it's first and only argument" 1>&2
fi

ssh-keygen -t rsa -b 2048 -C "bob" -f bob_key -N ''

mkdir -p /home/bob/.ssh
cp bob_key.pub /home/bob/.ssh/authorized_keys
chown -R bob:bob /home/bob/.ssh
chmod 0700 /home/bob/.ssh
chmod 0600 /home/bob/.ssh/authorized_keys

echo "private key for sending builds:"
cat bob_key

/letsencrypt/letsencrypt-auto certonly --webroot -w /var/www/html -d $1

sed 's/{{ server_name }}/$1/g' /nginx-pages/main > /etc/nginx/sites-enabled/main
