# laceworksdk_lql_dataset_handler

## Description

Execute LQL queries using the Lacework SDK.

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
|`type` | laceworksdk_lql_dataset_handler | `None` |
|`query_text` | the LQL query, all in a single line | `None` |
|`start_time` | start time for the query period | `None` |
|`end_time` | end time for the query period | `None` |

### Optional Fields

| Field | Description | Default |
|-------|-------------|---------|
|`subaccount` | use a subaccount context for the laceworkcli | `None` |
|`account` | use a specific account to connect to the lacework api. | `None` |
|`api_key` | use a specific api_key to connect to the lacework api. | `None` |
|`api_secret` | use a specific api_secret to connect to the lacework api. | `None` |
|`api_token` | use a specific api_token to connect to the lacework api. | `None` |

## Example

Execute the an LQL query for all external inbound connections:

```
{
    "name": "dataset1",
    "type": "laceworksdk_lql_dataset_handler",
    "organization": false,
    "start_time": "2021-12-29T00:00:00Z",
    "end_time": "2021-12-29T01:00:00Z",
    "query_text": "Custom_HA_Connections_1 { SOURCE { LW_HA_CONNECTIONS c } FILTER { NOT (STARTS_WITH(SRC_IP_ADDR,'10.')) AND NOT (STARTS_WITH(SRC_IP_ADDR,'192.168.')) AND NOT (STARTS_WITH(SRC_IP_ADDR,'127.')) AND NOT (STARTS_WITH(SRC_IP_ADDR,'172.16.')) AND NOT (STARTS_WITH(SRC_IP_ADDR,'172.17.')) AND NOT (STARTS_WITH(SRC_IP_ADDR,'172.18.')) AND NOT (STARTS_WITH(SRC_IP_ADDR,'172.19.')) AND NOT (STARTS_WITH(SRC_IP_ADDR,'172.20.')) AND NOT (STARTS_WITH(SRC_IP_ADDR,'172.21.')) AND NOT (STARTS_WITH(SRC_IP_ADDR,'172.22.')) AND NOT (STARTS_WITH(SRC_IP_ADDR,'172.23.')) AND NOT (STARTS_WITH(SRC_IP_ADDR,'172.24.')) AND NOT (STARTS_WITH(SRC_IP_ADDR,'172.25.')) AND NOT (STARTS_WITH(SRC_IP_ADDR,'172.26.')) AND NOT (STARTS_WITH(SRC_IP_ADDR,'172.27.')) AND NOT (STARTS_WITH(SRC_IP_ADDR,'172.28.')) AND NOT (STARTS_WITH(SRC_IP_ADDR,'172.29.')) AND NOT (STARTS_WITH(SRC_IP_ADDR,'172.30.')) AND NOT (STARTS_WITH(SRC_IP_ADDR,'172.31.')) AND c.SYN ='Incoming' } RETURN DISTINCT { c.RECORD_CREATED_TIME, c.MID, c.SRC_IP_ADDR, c.SRC_PORT, c.DST_IP_ADDR, c.DST_PORT, c.PROTOCOL, c.INCOMING, c.OUTGOING, c.FIRST_KNOWN_TIME } }",
    "filter": null
}
````