#!/bin/bash

docker run --rm -it \
    -v ~/.lacework.toml:/home/user/.lacework.toml \
    -v output:/app/output \
    -v reports:/app/reports \
    -v templates:/app/templates \
    --env=GCP_PROJECT=kubernetes-cluster-331006 \
    --env=GCP_ORG=286188307222 \
    --name custom-reporting \
    credibleforce/custom-reporting /bin/bash