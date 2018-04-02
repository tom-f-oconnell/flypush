#!/usr/bin/env bash

# TODO connect to vpn?

if [ ! -d dymo ]; then
    sudo apt install -y gcc g++ libcups2-dev libcupsimage2-dev
    mkdir dymo && cd dymo
    f=dymo-cups-drivers-1.4.0.tar.gz
    wget http://download.dymo.com/dymo/Software/Download\ Drivers/Linux/Download/$f
    tar xzf $f && rm $f
    cd dymo-cups-drivers-1.4.0.5
    ./configure
    make
    sudo make install
    cd ..
fi

# TODO automatically add any connected dymo to printers s.t. can be used w/ lpr?

sudo -H pip install -r requirements.txt

# TODO register script to start on startup, either to detect button presses or
# to constantly check camera feed for QR codes
