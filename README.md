# Just Effectively Formatting (JEF)

[![IMAGE ALT TEXT HERE](https://img.youtube.com/vi/AfIOBLr1NDU/0.jpg)](https://www.youtube.com/watch?v=AfIOBLr1NDU)

The aim of this project is to make it easier to build custom reports from data availbale via Lacework API and S3 Data Export.

## How It Works


## How To Run

The easiest way to run:

> `docker run -v ~/.lacework.toml:/home/user/.lacework.toml credibleforce/custom-reports`

This will mount your Lacework CLI credentials into the container and execute the scan on the default profile. You can, of course, pass in a different profile:

> ``

>> include examples of mounting report template and including environment variables

The script can also read the standard Lacework CLI environment variables for authentication.

## Known Issues


## Components

1) Yaml file that describes properties of each report to generate:
	1) `datasource` - where to get the data from:
		- `name`:
            * name of the datasource alias used in templates
		- `type`: 
			
            * `local` - directory, filename filter
			* `s3` - bucket, path, filename filter, credentials (stored in secret store attached to environment variable)
			* `lacework` - uri, token (stored in secret store attached to environment variable)
			* `generic` - uri, token (stored in secret store attached to environment variable)
		- `jq_filter`: 
            - filter the json result or get a count from an aggregated result
	2) `template` - a jinja formatted file. datasource name is array of json objects.
	3) `output`
			- `name`:
                * name of the output will be used in filename
			- `type`:
				- `local` - path
				- `s3` - bucket name, path, credentials (stored in secret store attached to environment variable)
2) Template file - jinja fomatted file that can be used to produce reports from template and existing data sources

## Workflow

1) spin up docker image
2) install lacework cli (curl https://raw.githubusercontent.com/lacework/go-sdk/main/cli/install.sh | bash)
3) install awscli
4) install python3, jq, jinja template
5) read data from source as object, apply filters
6) pass data objects to jinja template file
7) write output file to local or s3


## Future

1) web front-end via github
2) web front-end via lambda and s3