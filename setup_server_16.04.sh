#!/usr/bin/env bash

sudo apt update
sudo apt-get install -y postgresql libpq-dev postgresql-client \
    postgresql-client-common

# TODO how to best automatically add user? auth?
sudo adduser flypush --gecos "" --disabled-password
echo "flypush:flypush" | sudo chpasswd

sudo -u postgres psql -f create_db_and_role.sql
sudo -u flypush psql -f setup.sql
