#!/bin/sh
{
    echo "This script requires superuser access to install apt packages."
    echo "You will be prompted for your password by sudo."

    # clear any previous sudo permission
    sudo -k

    # run inside sudo
    sudo sh <<SCRIPT
    set -e
    echo "updating apt-get..."
    apt-get update 1>/dev/null
    echo "installing software-properties-common git python3.5 libssl-dev libpcre3-dev..."
    apt-get -y install software-properties-common git python3.5 libssl-dev libpcre3-dev 1>/dev/null
    add-apt-repository -y ppa:nginx/development
    apt-get update 1>/dev/null
    echo "installing the latest nginx..."
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
