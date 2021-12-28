# laceworkcli_dataset_handler

## Description

Execute laceworkcli commands and capture the JSON output.

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
|`type` | s3_dataset_handler | `None` |
|`s3_path` | path to the s3 bucket json (e.g. s3://example/myjson.json.gz). Wildcards and jinja date templates are excepted. | `None` |
|`newline_separated` | whether or not the json data in the buck is newline seerated for object (e.g. multiple object in one file, not in an array but newline separated) | `None` |
|`last_modified_begin` | the earliest modified data accepted | `None` |
|`last_modified_end` | the latest modified data accepted | `None` |

### Optional Fields

| Field | Description | Default |
|-------|-------------|---------|
|`profile` | the aws profile to use | `None` |

## Example

Connect to the s3 bucket `s3://proservlab-lacework-data/agent/2021-11-22/2021-11-22-05-00/"` using the aws profile `root` and read the `container_summary.json.gz` file. The json file is expected to have muitple json objects newline separated. Only files that have modification dates between `2021-11-01T00:00:00` and `2021-12-11T00:00:00`.

```
{
    "name": "dataset1",
    "type": "s3_dataset_handler",
    "s3_path": "s3://proservlab-lacework-data/agent/2021-11-22/2021-11-22-05-00/container_summary.json.gz",
    "newline_separated": true,
    "profile": "root",
    "last_modified_begin": "2021-11-01T00:00:00",
    "last_modified_end": "2021-12-11T00:00:00"
}
````