#!/bin/bash

set -e

HOME=/www/https
cd ${HOME}

echo "1.clear cache..."
rm -r *
echo "2.generate account.key"
openssl genrsa 4096 > account.key
echo "3.generate domain.key"
openssl genrsa 4096 > domain.key
echo "4.generate domain.csr"
openssl req -new -sha256 -key domain.key -subj "/" -reqexts SAN -config <(cat /etc/ssl/openssl.cnf <(printf "[SAN]\nsubjectAltName=DNS:wuaiwow.com,DNS:www.wuaiwow.com")) > domain.csr
echo "5.generate signed.crt"
python /usr/local/bin/acme_tiny.py --account-key ./account.key --csr ./domain.csr --acme-dir /var/www/challenges/ > ./signed.crt
echo "6.generate schained.pem"
wget -O - https://letsencrypt.org/certs/lets-encrypt-x3-cross-signed.pem > intermediate.pem
cat signed.crt intermediate.pem > chained.pem
echo "7.generate full_chained.pem"
wget -O - https://letsencrypt.org/certs/isrgrootx1.pem > root.pem
cat intermediate.pem root.pem > full_chained.pem
echo "8.generate dhparams.pem"
openssl dhparam -out dhparams.pem 2048
echo "9.relaod nginx"
service nginx reload
echo "10.Done."