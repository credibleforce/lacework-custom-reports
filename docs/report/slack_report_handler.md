# slack_report_handler

## Description

Output the template rendered data to a slack channel.

## Configuration Options

**Note**: The report configuration file does accept five jinja templating options. 

* `{{ env['VALUE'] }}` can be used to access environment variables.
* `{{ date.strftime('%Y-%m-%d') }}` provides access to the current date.
* `{{ delta1d }}` provides access to the current timedelta objects which can be used for date math, this provides 1d timedelta.
* `{{ delta1h }}` provides access to the current timedelta objects which can be used for date math, this provides 1h timedelta.
* `{{ delta30d }}` provides access to the current timedelta objects which can be used for date math, this provides 30d timedelta.

### Required Fields

| Field | Description | Default |
|-------|-------------|---------|
|`name` | name of the dataset | `None` |
|`type` | slack_report_handler | `None` |
|`token` | slack token | `None` |

### Optional Fields

| Field | Description | Default |
|-------|-------------|---------|
|`attachment_template` | format the attachment using the defined template | `None` |
|`attachment_name` | the filename of the attachment | `None` |
|`attachment_comment` | the comment for the attachment | `None` |

## Example

Output to a slack channel called `log`. Result should an attachment and formatted using the `./templates/html/table_simple.html.j2` template with the name `report.html`. Attachment comment `report`.

```
{
    "name": "slack",
    "type": "slack_report_handler",
    "token": "{{ env['TEST_TOKEN'] }}",
    
    "channel": "log"
}
````