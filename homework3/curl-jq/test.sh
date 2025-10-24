#!/bin/bash

API=http://dx.jxqz.org:8080/api


curl -s "${API}/spots?band=10m&frequency_min=29600.0&frequency_max=29700.0" 2> /dev/null | jq
