# Lacework Custom Reporting

The aim of this project is to make it easier to build custom reports from data availbale via Lacework API and S3 Data Export.

## How It Works

### Report Config and Templates

Lacework data source contain valuable information for reporting. These sources include the console API, S3 Data Export and Snowflake Data Share. In order to access these data sources and produce reports this project provides two configuration files:

* Report Config - This file contains a listing of the Dataset Handlers, Filters, Templates and Report Handlers used to create one or more reports.
* Report Template - These files are jinja template files that work in conjuntion with the data obtained from the data source.

### Dataset Handlers

This project contains multiple examples of Data Source Handlers but is written for community members to contribute additional plugins as required. Out of the box these Dataset Handlers are available:

* laceworkcli_dataset_handler - Pass command line arguements to the laceworkcli and capture the JSON output.
* laceworksdk_host_vuln_dataset_handler - Example usage of the python SDK to retrieve vulnerability data from the lacework API.
* local_dataset_hanlder - Read json data from a local file.
* s3_dataset_handler - Read one or more JSON files from an S3 bucket. Written to be used with Lacework S3 Data Export Data.

### Report Handlers

As with Data Source Handlers there are a number of pre-written Report Handlers. These handlers are use to write/output Dataset transformed data (e.g. write an HTML report to an S3 bucket). Out of the box these Report Handlers are available:

* local_report_handler - Write reports to the local file system. 
* s3_report_handler - Write reports to an S3 bucket.
* slack_report_handler - Write reports (as attachments) to a slack message. 

### Templates

Lastly there area a number of example jinja templates for various Report examples. These include:

* table_simple.html.j2 - Write a &lt;table&gt; from the Dataset data provided.
* table_advanced_dataframe.html.j2 - Write a &lt;table&gt; element from a Pandas Dataframe formatted json object. 
* table_advanced_boostrap_dataframe.html.j2 - Write a dynamic bootstrap-table from a Pandas Dataframe formatted json object.
* gcp_compliance_summary_report.html.j2 - Example rendering of an HTML version of the Lacework PDF compliance report.
* advanced_compliance_summary.html.j2 - Example of rendering multiple bootstap-tables from multiple Pandas Dataframe formatted objects.

## How To Run

The easiest way to run is using Docker. The included run.sh file demonstrates mounting lacework credentials and report directories. The result will be a HTML version of the `GCP compliance report` in the local `output` folder:

```
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
    credibleforce/lacework-custom-reports:latest --config /app/reports/laceworkcli/laceworkcli_gcp_compliance_html_report.json
```

## Known Issues

None at this time.

## Future

* Plugin Support
* Inline LQL Support
* Web Interface for Drag and Drop Config