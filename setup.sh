#!/usr/bin/env bash
# should be run as root

ssh-keygen -t rsa -b 2048 -C "bob" -f bob_key -N ''

mkdir -p /home/bob/.ssh
cp bob_key.pub /home/bob/.ssh/authorized_keys
chown -R bob:bob /home/bob/.ssh
chmod 0700 /home/bob/.ssh
chmod 0600 /home/bob/.ssh/authorized_keys

echo "private key for sending builds:"
cat bob_key

cd letsencrypt
./letsencrypt-auto certonly --webroot -w /var/www/html -d $1

sed 's/{{ server_name }}/$1/g' nginx-conf/main > /etc/nginx/sites-enabled/main
