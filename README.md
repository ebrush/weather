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

## Getting started
1. Working directory should be this project directory for all operations.
2. `python -m venv venv`
3. `source venv/bin/activate`
4. `pip install -r requirements.txt`

## Examples of supported functionality
### Running the local server and viewing API Swagger docs
1. `python manage.py runserver`
2. navigate to http://127.0.0.1:8000/api/weather/swagger/

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
`pytest`

### Creating HTML test coverage report
`pytest --cov=. --cov-report html`


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
* Instead of skipping duplicates, a file with same data is simply updated rather than duplicate skipped. This is faster than checking every row, and also means that the same file can be ingested multiple times without issue. It also has the bonus of being able to easily update existing data at a later time.
* Rather than convert fractions of celsius and millimeters to standard units to store, original units are kept to preserve accuracy. Conversion and rounding is performed on final calculations. The units that are used are documented in Swagger API docs and help_texts in the models file.


## Future Improvements
* remove secret_key from repo, place in a separate configuration
* rotate log files

## AWS Deployment Plan
