#!/usr/bin/env bash
set -e

if [ ! "env:$TRAVIS_BRANCH" == "env:master" ]; then
    echo not on master, not deploying
    exit 0
fi

echo "on master ✓"

if [ -z "$domain" ]; then
    echo "domain" variable not set
    exit 1
fi
echo "domain: $domain ✓"

echo "zipping _site to site.zio..."
(cd _site/ && zip -r - .) > site.zip 2>/dev/null

echo "decrypting ssh key..."
openssl aes-256-cbc -k "$bob_key_pass" -in bob_key.enc -out bob_key -d
chmod 400 bob_key

echo "setting StrictHostKeyChecking for all domains..."
printf "Host *\n    StrictHostKeyChecking no\n" > ~/.ssh/config
chmod 400 ~/.ssh/config

echo "copying site to $domain..."
scp -i bob_key site.zip bob@$domain:site.zip
