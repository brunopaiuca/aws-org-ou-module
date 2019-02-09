#!/bin/sh

V=1 

until [ "${V}" == '' ] ; 

  do

    V=$(python /srv/ou_provisioner.py)
    echo $V 
    sleep 1

  done
