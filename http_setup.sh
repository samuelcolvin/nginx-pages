#!/usr/bin/env bash
set -e
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 1>&2
   exit 1
fi

if [ -z "$1" ]
  then
    echo "This script requires your domain as it's first and only argument" 1>&2
fi

letsencrypt --webroot -w /var/www/html -d $1

sed 's/{{ server_name }}/'"$1"'/g' /nginx-pages/nginx-conf/main > /etc/nginx/sites-enabled/main

nginx -t

systemctl restart nginx
systemctl restart watch
