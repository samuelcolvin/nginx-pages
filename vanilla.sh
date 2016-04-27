#!/bin/sh
{
    set -e
    apt-get update
    apt-get -y install software-properties-common git python3.5 libssl-dev libpcre3-dev
    add-apt-repository -y ppa:nginx/development
    apt-get update
    apt-get install -y nginx
    rm -rf /var/lib/apt/lists/*
    chown -R www-data:www-data /var/lib/nginx

    git clone https://github.com/samuelcolvin/nginx-pages /nginx-pages
    git clone https://github.com/letsencrypt/letsencrypt /letsencrypt

    useradd -m bob

    openssl dhparam -out dhparams.pem 2048

    cp /nginx-pages/nginx-conf/redirect /etc/nginx/sites-enabled/default
    cp /nginx-pages/watch.service /etc/systemd/system/

SCRIPT
}
