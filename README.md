# serverless-query

The serverless query app allows users to run simple queries against parquet files in S3.

## Setup
To make setup as easy as possible it is recommended to leverage
the provided docker images and helper scripts. Of course docker is not
required to run the app but detailing the individual steps is out of scope
for this document. For a hint look at both the Dockerfiles in the root directory.

It is recommended you proceed through this section in order.

### Prerequisites
* AWS Account
* AWS Access Key with appropriate permissions (for now AdministratorAccess,
  though actual permissions required are more limited... IAM/S3/Lambda/CloudFormation/etc.)
* Docker
* AWS Access Key environment variables must be set.
  While there are other ways to set your aws creds (such as ~/.aws/credentials),
  these instructions assume that you have these set as environment variables
  to make running the docker commands simplier.
* git clone the repository: `git clone git@github.com:nxn128/serverless-query.git`

### Deploy Infrastructure
The infrastructure is defined with AWS SAM (CloudFormation)
To build and deploy the infrastructure (lambda functions, s3 bucket):
1. Run the helper script `sh ./build_and_deploy_infra.sh` from the root of the project.
   This checks you have your AWS envars set up and builds and runs the `deploy.Dockerfile`
   in the root of the project. This runs `sam build` and `sam deploy`.
1. Take a note of the `QueryDataBucket` output value since you will use that in your queries
   when specifying where you are selecting `FROM`.

### Build CLI
Run sh ./build_cli.sh from the root of the project to build the cli docker image

### Upload Data
The CLI provides functionality to allow you to upload data files from a URL into the `QueryDataBucket`. Local file uploads are not supported at this time.

For example if you wish to query `https://github.com/cwida/duckdb-data/releases/download/v1.0/taxi_2019_04.parquet` you should run the following command:

`docker run -t -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY cli python upload.py -f https://github.com/cwida/duckdb-data/releases/download/v1.0/taxi_2019_04.parquet -t uploads/taxi_2019_04.parquet`

See the [Parameters](#parameters) section for more details on upload parameters.

### Query Data
The CLI provides functionality to allow you to query the data and display the results in a few ways.

Assuming you have uploaded the file above from the **Upload Data** section,
you query it and output results to the terminal with the following command,
replacing `<QUERYDATABUCKET OUTPUT VAL>` with the bucket name from the `QueryDataBucket` output.

`docker run -t -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY cli python query.py -q "SELECT * FROM 's3://<QUERYDATABUCKET OUTPUT VAL>/uploads/taxi_2019_04.parquet';" -l 10`

This will also output the runtime of the query in ms.

See the [Parameters](#parameters) section for more details on query options.

## Parameters
### query.py
The following parameters are available to the query.py script:
* **--query** or **-q**: SQL query to execute in a quoted string
* **--limit** or **-l**: Limits the max number of rows to return (capped at 1000)
* **--output** or **-o**: Filename to write output in csv format
* **--interactive** or **-i**: Extremely primative REPL for executing queries interactively at a prompt

### upload.py
The following parameters are available to the upload.py script:
* **--from-url** or **-f**: URL to retrieve data for upload from
* **--to** or **-t**: Path and filename of where to upload data.
  Bucket name is not configurable.

## Docker command details
When running a docker command there are a number of parameters that may be
confusing. While the definitive definitions can be found in the docker
documentation, a brief explaination of the run command parameters above:

* **-t**: The output is written to the terminal. This indicates things like
  including color codes
* **-e**: Set this environment variable in the docker container. Because there
  is no value specified this indicates to grab the value from your current session
  and inject that.

## Architecture
The architecture is currently very simple and at a high-level
can be seen in the diagram below:

![Serverless query architecture](./query.png?raw=true "Serverless query architecture")

Top-level dependencies:

* boto3: AWS SDK
* duckDb: DB Engine
* click: CLI
* rich: Table display in terminal
* prompt_toolkit: REPL
* requests: Download external data from url
* pytest: unit tests

## Limitations
* Queries can currently return no more than 1000 records.
* Pagination is "manual" in that while limit can be passed in
  offset cannot currently and all records gather are returned
  (up to the 1000 record max)


## Future improvements
In no particular order:

* Support unlimited query size (would involve multiple lambda calls and lambda streaming output). Interestingly: https://aws.amazon.com/blogs/compute/introducing-aws-lambda-response-streaming/.
* Syntax highlighting / parsing in the REPL
* Query "replay", save queries and allow quick re-running (though better UI would likely be a better choice)
* Report telemetry data out
* Support local file uploads
* Web UI layer for data visualization / "notebook" support (how would this differ from Jupyter notebooks that can already connect to duckdb?)
* More / better unit tests
* Integration tests
* Package the CLI so it can be installed by pip
* Paging could be improved (though what is the use case for tabbing through terminal data? If we have pages just export to csv or something else for analysis). Currently relies on user to submit query with LIMIT and OFFSET.
* Perhaps changing from `fetchmany` to `fetch_df` to return more metadata with records
