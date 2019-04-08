#!/bin/bash

set -e

cd /var/www/challenges
python acme_tiny.py --account-key account.key --csr domain.csr --acme-dir /var/www/challenges > signed.crt || exit
wget -O - https://letsencrypt.org/certs/lets-encrypt-x3-cross-signed.pem > intermediate.pem
cat signed.crt intermediate.pem > chained.pem
# service nginx reload