#!/bin/sh
{
    echo "This script requires superuser access to install apt packages."
    echo "You will be prompted for your password by sudo."

    # clear any previous sudo permission
    sudo -k

    # run inside sudo
    sudo sh <<SCRIPT

    set -e

    echo "installing add-apt-repository..."
    apt-get -y install software-properties-common python-software-properties 1>/dev/null

    echo "adding apt repository ppa:nginx/development..."
    add-apt-repository -y ppa:nginx/development

    echo "updating apt-get..."
    apt-get update 1>/dev/null

    echo "installing the latest nginx..."
    apt-get install -y nginx 1>/dev/null
    chown -R www-data:www-data /var/lib/nginx

    echo "installing other requirements: git python3 libssl-dev libpcre3-dev..."
    apt-get -y install git python3 libssl-dev libpcre3-dev 1>/dev/null

    echo "cloning nginx-pages and letsencrypt..."
    git clone https://github.com/samuelcolvin/nginx-pages /nginx-pages 1>/dev/null
    git clone https://github.com/letsencrypt/letsencrypt /letsencrypt 1>/dev/null

    echo "adding using "bob" - the builder..."
    useradd -m bob

    cp /nginx-pages/nginx-conf/redirect /etc/nginx/sites-enabled/default
    cp /nginx-pages/watch.service /etc/systemd/system/

    echo "generating unique primes for ssl, this might be very slow. Hold tight..."
    openssl dhparam -out /nginx-pages/dhparams.pem 2048

SCRIPT
}
