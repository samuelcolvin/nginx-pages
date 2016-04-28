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
