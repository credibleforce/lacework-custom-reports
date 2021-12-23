#!/bin/bash

docker run --rm \
    -v ~/.lacework.toml:/home/user/.lacework.toml \
    -v $(pwd)/output:/app/output \
    -v $(pwd)/reports:/app/reports \
    -v $(pwd)/templates:/app/templates \
    --env=GCP_PROJECT=kubernetes-cluster-331006 \
    --env=GCP_ORG=286188307222 \
    --name custom-reporting \
    credibleforce/custom-reporting --config /app/reports/laceworkcli/laceworkcli_gcp_compliance_html_report_docker.json