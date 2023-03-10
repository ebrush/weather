import datetime
import logging
import re
from collections.abc import Iterator
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db.models import F, Sum, Avg

from history.models import WeatherDay, WeatherStation, WeatherStats

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Loads weather data from station files'

    def add_arguments(self, parser):
        parser.add_argument('path', type=str,
                            help='Path to input file or directory '
                                 'containing files. Subdirectories '
                                 'will not be processed.')

    def handle(self, *args, **options):
        logger.info({'msg': 'ingestion started', 'path': options['path']})
        num_records_ingested = 0
        num_files_processed = 0

        # iterate through all files in the directory, or just the one file
        #  if a specific file was given
        for num_files_processed, filepath in enumerate(
                self.iter_files_to_process(options['path']), 1):

            # create the weather station object
            #  with its code set based on the filename of the data
            station = WeatherStation.objects.get_or_create(
                defaults={'code': filepath.stem},
                code=filepath.stem
            )[0]

            # create WeatherDay objects based on the rows in the text file
            weather_days_to_create = self.convert_file_rows_to_database_rows(
                station, filepath
            )

            # consider what years were in the file in order to update
            #  only the statistics affected by those years
            years_to_update = {weather_day.date.year for weather_day
                               in weather_days_to_create}

            # update the database in bulk for our particular station
            num_records_ingested += len(WeatherDay.objects.bulk_create(
                weather_days_to_create,
                update_conflicts=True,
                update_fields=('temperature_max', 'temperature_min',
                               'precipitation'),
                unique_fields=('station', 'date'),
            ))

            # update the statistics that could be affected by this
            #  station's update
            self.update_statistics(station, years_to_update)

        logger.info(
            {'msg': 'ingestion finished', 'path': options['path'],
             'records_ingested': num_records_ingested,
             'files_processed': num_files_processed})

    def convert_file_rows_to_database_rows(self, station, filepath_to_load):
        """based on a station and a path to file, return WeatherDay instances"""
        rows = []
        dates_encountered = set()
        for (date, temperature_max,
             temperature_min,
             precipitation) in self.iter_rows_to_process(
            str(filepath_to_load)):
            date = datetime.datetime.strptime(date, '%Y%m%d').date()
            if date in dates_encountered:
                continue
            weather_day = WeatherDay(
                station=station,
                date=date,
                temperature_max=temperature_max,
                temperature_min=temperature_min,
                precipitation=precipitation,
            )
            self.log_message_if_some_data_missing(weather_day)
            rows.append(weather_day)
            dates_encountered.add(date)
        return rows

    def iter_files_to_process(self, path: str) -> Iterator[Path]:
        """for user's input path, yield each filepath needing processing"""
        path = Path(path)

        if not path.exists():
            raise CommandError('provided path does not exist')

        if path.is_dir():
            for file_path in path.iterdir():
                if file_path.is_dir():
                    logger.warning({'msg': 'skipping subdirectory',
                                    'path': str(file_path)})
                    continue
                yield file_path
        else:
            yield path

    def iter_rows_to_process(self, filepath_to_load: str):
        """for a file needing processing, yield each row as raw data"""
        with open(filepath_to_load, 'r') as f:
            for line in f:
                columns = re.findall(r'\S+', line)
                for i, column in enumerate(columns):
                    if column == '-9999':
                        columns[i] = None
                yield columns

    def log_message_if_some_data_missing(self, weather_day: WeatherDay):
        """check if any fields are null in a WeatherDay and log if so"""
        if (weather_day.temperature_max is None
                or weather_day.temperature_min is None
                or weather_day.precipitation is None):
            logger.warning({
                'msg': 'ingesting a row with missing data',
                'missing_temperature_max': weather_day.temperature_max is None,
                'missing_temperature_min': weather_day.temperature_min is None,
                'missing_precipitation': weather_day.precipitation is None,
                'station': weather_day.station.code,
                'date': weather_day.date,
            })

    def update_statistics(self, station, years_to_update):
        """for a station and the given years, recalculate and save stats"""
        stats_to_update = []

        for r in WeatherDay.objects.filter(
                station=station, date__year__in=years_to_update).values(
            'date__year').annotate(
            avg_temperature_max_celsius=Avg(F('temperature_max') / 10.0),
            avg_temperature_min_celsius=Avg(F('temperature_min') / 10.0),
            total_precipitation_centimeters=Sum(F('precipitation') / 100.0)):
            stats_to_update.append(WeatherStats(
                station=station,
                year=r['date__year'],
                avg_temperature_max=r['avg_temperature_max_celsius'],
                avg_temperature_min=r['avg_temperature_min_celsius'],
                total_precipitation=r['total_precipitation_centimeters'],
            ))

        WeatherStats.objects.bulk_create(
            stats_to_update,
            update_conflicts=True,
            update_fields=('avg_temperature_max', 'avg_temperature_min',
                           'total_precipitation'),
            unique_fields=('station', 'year'),
        )
