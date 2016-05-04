# nginx-pages

Github pages inspired static site server using [nginx](https://www.nginx.com/resources/wiki/),
and scp. It defaults to https using [letsencrypt](https://letsencrypt.org/) to grant certificates.

The build script installs latest nginx to support http2.

### Install

    sudo apt-get update && sudo apt-get install wget
    wget -O- https://raw.githubusercontent.com/samuelcolvin/nginx-pages/master/vanilla.sh | sh

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
