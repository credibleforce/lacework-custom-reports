# local_report_handler

## Description

Output the template rendered data to the local filesystem.

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
|`path` | file path location for the output templated data | `None` |

## Example

Output the report to `./output/gcp_compliance_report.html`

```
{
    "name": "output",
    "type": "local_report_handler",
    "path": "./output/gcp_compliance_report.html"
}
````