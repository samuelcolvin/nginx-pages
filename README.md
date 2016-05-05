# nginx-pages

## What

Github pages inspired static site server which can run on your own server and deploy automatically using CI.

## Why

Static sites builders like jekyll are very cool and deploying them using github pages is very convenient,
however HTTPS is becoming more and more important for SEO.

HTTPS isn't the only win you get by moving beyond github pages; there are a myriad of other reasons
why you might want the flexibility of deploying your site on a server you control.

We want the easy of updating sites with github pages while deploying to a server under our command.

The advent of very cheap, easy to use virtual servers and free CI means you can deploy on your
own server for just a few 4/£/€ a month.

## How

nginx-pages uses:

* [nginx](https://www.nginx.com/resources/wiki/) to serve static files
* [letsencrypt](https://letsencrypt.org/) to generate signed SSL certificates easily and for free.
* [travis](https://travis-ci.org/) to build the site, check it's good and send the freshly built site to your server. Other CI services and manual deploy should work fine too.
* [jekyll](https://jekyllrb.com/) to build your site. [Other](https://www.staticgen.com/) static site generates should work fine too, but the example below assumes jekyll.
* [scp](https://en.wikipedia.org/wiki/Secure_copy) to transfer the built site to your server, travis's encrypted environment variables mean this works even with public repos, see below.
* [http2](https://en.wikipedia.org/wiki/HTTP/2) the `vanilla.sh` install script installs the latest version of nginx which supports the much improved new version of http.
* [scaleway](https://www.scaleway.com/) are a great option as their virtual server at €2.99/month are very cheap. Note: nginx-pages doesn't work with their "C1" arm based bare metal servers as their hardware doesn't support ipv6 which nginx expects.

The basic work flow of setting up nginx-pages is very simple:

1. install requirements on a fresh Ubuntu virtual server
1. Use the script below to create a new user with limited permissions who can scp new sites to your server
1. Use the script below to setup nginx with the right sites.
1. scp a `site.zip` site to the server and it should be automatically deployed.

### Install

This has been tested on a fresh install of Ubuntu 16.04 LTS.

    sudo apt-get update && sudo apt-get install wget
    wget -O- https://raw.githubusercontent.com/samuelcolvin/nginx-pages/master/vanilla.sh | sh

In theory a machine image could be taken at this point and reused on different servers,
but I haven't got round to that yet.

### Setup

You now need to setup scp and nginx, to setup scp:

    sudo /nginx-pages/scp_setup.sh

Which should create an ssh key for the user "bob" and print it to the terminal, the file itself will
be available in working directory as `bob_key`. You'll use this key later to transfer new sites to the server.
You'll want to copy & paste it or scp it back to your machine.

Setup nginx (the http server):

    sudo /nginx-pages/http_setup.sh www.example.com

(where you obviously want to replace `www.example.com` with your domain)

This will use letsencrypt to create ssh keys and setup nginx to use them.

**done**

The watch service should now be live (you can check with `systemctl status watch`) and nginx running.

If you write to `/home/bob/site.zip` the contents should be extracted and then served by nginx.

Every site build adds a `build.txt` file which gives some details on the most recent build.
See [https://tutorcruncher.com/build.txt](https://tutorcruncher.com/build.txt) for an example.

### Deploying Builds

You should now be able to deploy to your server using scp, note the zip command to make sure the root
directory of the zip file is correct. Here we assume you're using jekyll so the built site is in `_sites`.

    #> (cd _site/ && zip -r - .) > site.zip
    #> scp -i bob_key site.zip bob@www.example.com:site.zip

(assuming you have the `bob_key` file from above in your working directory)

### Deploying using travis

Travis allows you to create [encrypted files](https://docs.travis-ci.com/user/encrypting-files/) which
are not available in fork pull requests.

This in turn allows you to encrypt the private key `bob_key` generated above. Once you have the
[travis cli](https://github.com/travis-ci/travis.rb) installed and have download `bob_key` to the root git
directory of the site you wish to deploy run:

```shell
# to create a string random password
bob_key_pass="$(openssl rand -base64 32)"
# print the password for your reference (you probably won't need to know it at any point)
echo "bob_key_pass = $bob_key_pass"
# encypt bob_key with the password and delete the original
openssl aes-256-cbc -k $bob_key_pass -in bob_key -out bob_key.enc
rm bob_key
# add bob_key_pass as a secure variable to .travis.yml
travis encrypt bob_key_pass=$bob_key_pass --add
# download deploy.sh
curl https://raw.githubusercontent.com/samuelcolvin/nginx-pages/master/deploy.sh > deploy.sh
chmod a+x deploy.sh
```

This should have automatically edited your `.travis.yml` file, you'll need to edit it further to call
`deploy.sh`. In the end the file should look something like:

```yml
language: ruby
rvm:
- 2.1
script:
- bundle exec jekyll build
- bundle exec htmlproofer _site
env:
  global:
  - NOKOGIRI_USE_SYSTEM_LIBRARIES=true
  - domain: <your domain name>
  - secure: <your secure variable for bob_key_pass>
after_success:
  - ./deploy.sh
```

(this is an example with site build using jekyll, see https://github.com/tutorcruncher/tutorcruncher.com
for a full example)

### Modifying the nginx site conf

You might want to modify the `/etc/nginx/sites-enabled/main` eg. to tell nginx to your your own `404.html`.

```
    ...
    error_page 404 /404.html;

     location = /404.html {
        root /var/www/html;
        internal;
    }
}
```

### To debug the watch service

(Really just a note for me, with luck you can ignore this)

A few useful commands when debugging the watch service (or indeed any other service):

```shell
# a summary of the current status of watch
service watch status
# to restart watch (will rebuild the site)
service watch restart

# journalctl live
journalctl -f
# journalctl live filtered to just this watch.service
journalctl -f _SYSTEMD_UNIT=watch.service
# journalctl live showing only error level logs
journalctl -f -p err
```

`journalctl` can also show important information about `nginx`  and `sshd`.
