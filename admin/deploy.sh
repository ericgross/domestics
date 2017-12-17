#!/bin/bash

pwd=`dirname $0`

ansible-playbook $pwd/lights.yml
