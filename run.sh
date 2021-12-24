#!/bin/bash

docker run --rm -it \
    `# name of the container` \
    --name custom-reporting \
    `# mount credentials and configuration` \
    -v ~/.lacework.toml:/home/user/.lacework.toml \
    -v $(pwd)/output:/app/output \
    -v $(pwd)/reports:/app/reports \
    -v $(pwd)/templates:/app/templates \
    `# report environment variables` \
    --env=GCP_PROJECT=kubernetes-cluster-331006 \
    --env=GCP_ORG=286188307222 \
    `# override the uid to allow docker write through to output volume (optional)` \
    --env=HOME=/home/user \
    --user $UID:$GID \
    `# run the report script` \
    credibleforce/custom-reporting:main --config /app/reports/laceworkcli/laceworkcli_gcp_compliance_html_report.json