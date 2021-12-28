# laceworkcli_dataset_handler

## Description

Execute laceworkcli commands and capture the JSON output.

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
|`type` | laceworkcli_dataset_handler | `None` |
|`command` | laceworkcli command (e.g. compliance, vulnerability) | `None` |
|`args` | laceworkcli command args (see lacework --help) | `None` |
|`organization` | use the organization context for the laceworkcli | `False` |

### Optional Fields

| Field | Description | Default |
|-------|-------------|---------|
|`subaccount` | use a subaccount context for the laceworkcli | `None` |
|`account` | use a specific account to connect to the lacework api. | `None` |
|`api_key` | use a specific api_key to connect to the lacework api. | `None` |
|`api_secret` | use a specific api_secret to connect to the lacework api. | `None` |
|`api_token` | use a specific api_token to connect to the lacework api. | `None` |
|`profile` | use a specific profile to connect to the lacework api. | `None` |

## Example

Execute the lacework cli to retrieve the GCP compliance report:

`lacework compliance gcp get-report {{ env['GCP_ORG']}} {{ env['GCP_PROJECT'] }} --json`

```
{
    "name": "dataset1",
    "type": "laceworkcli_dataset_handler",
    "command": "compliance",
    "args": "gcp get-report {{ env['GCP_ORG'] }} {{ env['GCP_PROJECT'] }}",
    "organization": false,
}
````