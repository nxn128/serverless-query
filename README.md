# serverless-query

The serverless query app allows users to run simple queries against parquet files in S3.

## Setup
To make setup as easy as possible it is recommended to leverage
the provided docker images and helper scripts.

If docker is not feasible please see the [Advanced Setup](#advanced-setup) section
for more information on what needs to be installed (or peek at the Dockerfiles).

It is recommended you proceed through this section in order.

### Prerequisites
* AWS Account
* AWS Access Key with appropriate permissions (for now AdministratorAccess,
  though actual permissions required are more limited... IAM/S3/Lambda/CloudFormation/etc.)
* Docker must be installed and running
* AWS Access Key environment variables must be set `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`.
  While there are other ways to set your aws creds (such as ~/.aws/credentials),
  these instructions assume that you have these set as environment variables
  to make running the docker commands simplier.
* `git` is installed
* git clone the repository: `git clone git@github.com:nxn128/serverless-query.git` to a local directory

### Deploy Infrastructure
The infrastructure is defined with AWS SAM (CloudFormation)
To build and deploy the infrastructure (lambda functions, s3 bucket):
1. Run the helper script `sh ./build_and_deploy_infra.sh` from the root of the project.
   This checks you have your AWS envars set up and builds and runs the `deploy.Dockerfile`
   in the root of the project. This runs `sam build` and `sam deploy`.
1. Take a note of the `QueryDataBucket` output value since you will use that in your queries
   when specifying where you are selecting `FROM`.

### Build CLI
Run `sh ./build_cli.sh` from the root of the project to build the cli docker image

### Upload Data
The CLI provides functionality to allow you to upload data files from a URL into the `QueryDataBucket`. Local file uploads are not supported at this time.

For example if you wish to query `https://github.com/cwida/duckdb-data/releases/download/v1.0/taxi_2019_04.parquet` you should run the following command:

```
docker run -t -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY cli python upload.py -f https://github.com/cwida/duckdb-data/releases/download/v1.0/taxi_2019_04.parquet -t uploads/taxi_2019_04.parquet
```

See the [Parameters](#parameters) section for more details on upload parameters.

### Query Data
The CLI provides functionality to allow you to query the data and display the results in a few ways.

Assuming you have uploaded the file above from the **Upload Data** section,
you can query it and output results to the terminal with the following command,
replacing `<QUERYDATABUCKET OUTPUT VAL>` with the bucket name from the `QueryDataBucket` output.

```
docker run -t -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY cli python query.py -q "SELECT pickup_at, fare_amount, mta_tax FROM 's3://<QUERYDATABUCKET_OUTPUT_VAL>/uploads/taxi_2019_04.parquet';" -l 10
```

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
* duckdb: DB Engine
* click: CLI
* rich: Table display in terminal
* prompt_toolkit: REPL
* requests: Download external data from url
* pytest: unit tests

## Tests
There are currently only two unit test in the project, more will need to be added.

To run the tests run `pytest` from the base directory.

## Limitations
* Queries can currently return no more than 1000 records.
* Pagination is "manual" in that while limit can be passed in as a parameter
  offset cannot, but instead it currently relies on user to submit query with OFFSET.
  All records up to 1000 rows are returned in one chunk.
* When printing to the terminal, only the visible area is printed to,
  so some columns may not display if the table is wide. If the screen
  is expanded the query needs to be re-run. A min-width is set on the columns
  to allow the user to recognize some of the data.


## Future improvements
In no particular order:

* Support unlimited query size (would involve multiple lambda calls and lambda streaming output). Interestingly: https://aws.amazon.com/blogs/compute/introducing-aws-lambda-response-streaming/ but there are still limits in size per function execution.
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
* Add CI/CD pipeline with build, test, deploy, autoversioning
* Possibly create API Gateway layer, to make it easier for distributed scripts to call in be authenticated, throttled, etc. May not be relevant depending on where
  all artifacts live.


## Advanced Setup
If you wish to install on your local machine instead of using the docker images you will need the following...

### Prerequisites
* Install python 3.9.6 ([pyenv](https://github.com/pyenv/pyenv) highly recommended
* AWS Account
* AWS Access Key with appropriate permissions (for now AdministratorAccess,
  though actual permissions required are more limited... IAM/S3/Lambda/CloudFormation/etc.)
* Install the [AWS CLI](https://aws.amazon.com/cli/)
* Install [AWS SAM](https://aws.amazon.com/serverless/sam/)
* Ensure `git` is installed
* run `git clone git@github.com:nxn128/serverless-query.git`

Once you are ready, you can deploy the infra by navigating to the directory where you
cloned the repo and running:
* `sam build && sam deploy`

To get ready to run the CLI scripts:
* (Optional) Set up a [virtual environment](https://docs.python.org/3/library/venv.html)
   to prevent package conflicts
* run `pip3 install -r requirements.txt` from this top-level directory
* ensure you have an `AWS_DEFAULT_REGION` set to `us-east-2`

To run the `query` or `upload` scripts you can run `python src/query.py ...` or `python src/upload.py ...`

For details on commands to run to get started see the [Upload Data](upload-data) section
modifying the commmands to start the same as above vs calling `docker run ...`.
