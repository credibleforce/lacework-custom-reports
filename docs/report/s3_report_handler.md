# s3_report_handler

## Description

Output the template rendered data to an s3 bucket.

## Configuration Options

**Note**: The report configuration file does accept five jinja templating options. 

* `{{ env['VALUE'] }}` can be used to access environment variables.
* `{{ date.strftime('%Y-%m-%d') }} provides access to the current date.
* `{{ delta1d }}` provides access to the current timedelta objects which can be used for date math, this provides 1d timedelta.
* `{{ delta1h }}` provides access to the current timedelta objects which can be used for date math, this provides 1h timedelta.
* `{{ delta30d }}` provides access to the current timedelta objects which can be used for date math, this provides 30d timedelta.

### Required Fields

| Field | Description | Default |
|-------|-------------|---------|
|`name` | name of the dataset | `None` |
|`type` | s3_report_handler | `None` |
|`s3_path` | the s3 bucket path | `None` |
|`compressed` | gzip compress the resultant data | `False` |

### Optional Fields

| Field | Description | Default |
|-------|-------------|---------|
|`profile` | the aws profile | `None` |

## Example

Output the report to `s3://proservlab-report-bucket/Lacework/Compliance/{{ date.strftime('%Y-%m-%d') }}/{{ date.strftime('%Y-%m-%d-%H-%M') }}` using the aws profile `root`. Gzip compress the resultant file.

```
{
    "name": "output",
    "type": "s3_report_handler",
    "s3_path": "s3://proservlab-report-bucket/Lacework/Compliance/{{ date.strftime('%Y-%m-%d') }}/{{ date.strftime('%Y-%m-%d-%H-%M') }}/gcp_compliance_report.json",
    "profile": "root",
    "compressed": true
}
````