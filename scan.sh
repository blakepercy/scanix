#!/bin/bash
set +e

setalarm -s ~/scanix/etc/setalarm/systems.conf -k ~/scanix/etc/setalarm/keywords.conf -x ~/scanix/etc/setalarm/keywords-exclude.conf

