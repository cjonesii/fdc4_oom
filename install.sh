#!/bin/bash

## This script will check the packages that the project requires and install if not found

echo "Updating package sources"
apt-get update

echo "Checking required packages"
REQUIRED_PKG="python3 python3-pip"
for PKG in $REQUIRED_PKG; do
  PKG_OK=$(dpkg-query -W --showformat='${Status}\n' $PKG|grep "install ok installed")
  echo Checking for $PKG: $PKG_OK
  if [ "" = "$PKG_OK" ]; then
      echo "No $PKG. Setting up $PKG."
      echo "run as script apt-get --yes install $PKG"
  else echo "$PKG is already installed"
  fi
done

echo "Installing project requirements"
pip3 install -r requirements.txt

echo "Installing the project"
python3 setup.py install
