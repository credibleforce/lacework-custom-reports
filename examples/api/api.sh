#!/bin/bash

# retrieve token
# curl --header "Content-Type: application/json" \
#   --header "x-lw-uaks: {{ env['LACEWORK_SECRET'] }}" \
#   --request POST \
#   --data '{ "keyId": "{{ env['LACEWORK_KEY'] }}","expiryTime": 3600 }' \
#  https://lwps.lacework.net/api/v2/access/tokens

# use token to pull data from api
curl --header "Content-Type: application/json" \
  --header "Authorization: {{ env['LACEWORK_TOKEN'] }}" \
  --request GET \
  https://lwps.lacework.net/api/v2/UserProfile