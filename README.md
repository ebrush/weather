# Weather API

## Table of contents
* Requirements
* Getting Started
* Examples
* Documentation
* Logs
* Design Rationales
* Future Improvements
* AWS Deployment Plan

## Requirements
* Tested on Manjaro Linux
* Tested with Python 3.10.8
* Tested with SQLite3 and Postgres 15.2

## Getting started
1. Working directory should be this project directory for all operations.
2. `python -m venv venv`
3. `source venv/bin/activate`
4. `pip install -r requirements.txt`
5. (optional) setup PostgreSQL as shown below
6. `python manage.py migrate`
7. `python -m pytest`

SQLite3 will be used by default. PostgreSQL will be used automatically if you set the 5 DB_* environment variables in settings_base.py. I like to use postgres in docker to get started easily as shown. You may need to install the PostgreSQL client applications to use createuser, createdb, etc.

If you want to test PostgreSQL locally:

  docker run -d -e POSTGRES_PASSWORD=pgPass12345 -p 5432:5432 postgres:latest;
  createuser -d -U postgres -P -w -p 5432 -h 0.0.0.0 weatherman;
  createdb --owner=weatherman -w -p 5432 -U weatherman -W -h 0.0.0.0 weather;
  export DB_USER=weatherman;
  export DB_NAME=weather;
  export DB_HOST=0.0.0.0;
  export DB_PASSWORD=ThePasswordEnteredOnCreateUser;
  export DB_PORT=5432;

## Examples of supported functionality
### Running the local server and viewing API Swagger docs
1. `python manage.py runserver`
2. navigate to http://127.0.0.1:8000/api/weather/swagger/

JSON and yaml versions of the API spec can be downloaded by appending ".json" or ".yaml" to the Swagger url.

### Ingesting a single file
`python manage.py ingest_history path/to/weather_file.txt`

### Ingesting a directory (subdirectories not included)
`python manage.py ingest_history path/to/weather_directory`

### API Request examples
* See weather-history.postman_collection.json which can be imported into Postman.
* Query params can be removed and adjusted for desired filtering and navigation through pagination.
* More info on params are in the Swagger docs.
* Units of measure are documented in Swagger and Django Model's help_texts.
  * In the api/weather endpoint, the original units of measurement of the file are kept.
  * In the stats endpoint, the units are adjusted to celsius and centimeters.

#### Iterate days of weather
`GET http://127.0.0.1:8000/api/weather?station__code=USC00338552&date=1985-01-01&limit=10&offset=0`

    {
        "count": 1,
        "next": null,
        "previous": null,
        "results": [
            {
                "station": {
                    "code": "USC00338552"
                },
                "date": "1985-01-01",
                "temperature_max": 156,
                "temperature_min": 0,
                "precipitation": 58
            }
        ]
    }

#### Iterate years of weather by station to see weather stats
`GET http://127.0.0.1:8000/api/weather/stats?station__code=USC00338552&year=1985`

    {
        "count": 1,
        "next": null,
        "previous": null,
        "results": [
            {
                "station": {
                    "code": "USC00338552"
                },
                "year": 1985,
                "avg_temperature_max": "16.06",
                "avg_temperature_min": "3.17",
                "total_precipitation": "97.93"
            }
        ]
    }

### Applying code formatting
`yapf --in-place **/*.py`

### Running tests
`pytest` or `python -m pytest`

### Creating HTML test coverage report
`pytest --cov=. --cov-report html`
(last tested at >90%)

## Documentation
In several places, useful comments and info can be found. These include:
* docstrings
* help_texts in Models
* Swagger docs
* the postman collection in weather-history.postman_collection.json
* the django admin
  * `python manage.py createsuperuser`
  * `python manage.py runserver`
  * navigate to 127.0.0.1:8000/admin/


## Logs
Logs are created as a JSON object per entry.
By default, data ingestion logs to the console and the logs folder.
Logs are skipped during automated tests.


## Design rationales
### Duplicate handling
Duplicates are skipped within a single file upload, meaning that only the first row will be ingested. On subsequent uploads, if a row already exists in the database, it will be overwritten. This is faster than checking every row, and also means that the same file can be ingested multiple times without issue. It also has the bonus of being able to easily update existing data at a later time.

### Units of measures saved
Rather than convert fractions of celsius and millimeters to standard units to store, original units are kept to preserve accuracy. Conversion and rounding is performed on final calculations. The units that are used are documented in Swagger API docs and help_texts in the models file.

### SQLite3 and PostgreSQL
SQLite3 is the easiest and fastest to use for local testing, while PostgreSQL is performant, standards-compliant, and widely used and supported in many cloud environments. 


## Future Improvements
* Remove secret_key from repo, place in a separate configuration.
* Rotate log files.
* Depending on how the project is hosted, a file store may need to be mounted for the log files, or the logging could be changed to a cloud-based logging service.
* A way of triggering ingestion via API. This will allow more flexibility and help in deploying to different environments.
* Ways of ingesting non-local files. An AWS Lambda can read files from S3 or an FTP server, which may be necessary once the project is hosted, depending on where the files are located when provided.


## AWS Deployment Plan
The services I would use are:

Lambda - for serving the API. This will minimize costs of running the API
S3 - for storing the style files needed for the Swagger docs
CloudFront - for distributing the files in S3
RDS - for hosting a PostgreSQL instance
EventBridge - for scheduling a periodic ingestion of files by triggering a weather ingestion endpoint in the Lambda API


All services could be updated automatically with a CI script in Github or Gitlab. I prefer these to CircleCI since the repo is with the deployment code.
Preferably we would also have Terraform code for initially provisioning the services.
