import csv
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
        records_ingested_count = 0
        files_processed = 0
        for filepath_to_load in self.iter_files_to_process(options['path']):
            station = WeatherStation.objects.get_or_create(
                defaults={'code': filepath_to_load.stem},
                code=filepath_to_load.stem
            )[0]
            years_updated = set()

            weather_days_to_create = []
            for (date, temperature_max,
                 temperature_min,
                 precipitation) in self.iter_rows_to_process(filepath_to_load):
                date = datetime.datetime.strptime(date, '%Y%m%d').date()
                years_updated.add(date.year)
                temperature_max = (temperature_max
                                   if temperature_max != '-9999'
                                   else None)
                temperature_min = (temperature_min
                                   if temperature_min != '-9999'
                                   else None)
                precipitation = (precipitation
                                 if precipitation != '-9999'
                                 else None)
                if (temperature_max is None
                        or temperature_min is None
                        or precipitation is None):
                    logger.warning({
                        'msg': 'ingesting a row with missing data',
                        'missing_temperature_max': temperature_max is None,
                        'missing_temperature_min': temperature_min is None,
                        'missing_precipitation': precipitation is None,
                        'station': station.code,
                        'date': date,
                    })
                weather_days_to_create.append(WeatherDay(
                    station=station,
                    date=date,
                    temperature_max=temperature_max,
                    temperature_min=temperature_min,
                    precipitation=precipitation,
                ))
                records_ingested_count += 1
            WeatherDay.objects.bulk_create(
                weather_days_to_create,
                update_conflicts=True,
                update_fields=('temperature_max', 'temperature_min',
                               'precipitation'),
                unique_fields=('station', 'date'),
            )
            files_processed += 1

            stats_to_update = []
            for r in WeatherDay.objects.filter(
                    station=station, date__year__in=years_updated).values(
                    'date__year').annotate(
                    avg_temperature_max_celsius=Avg(F('temperature_max') / 10),
                    avg_temperature_min_celsius=Avg(F('temperature_min') / 10),
                    total_precipitation_centimeters=Sum(F('precipitation') / 100)):
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

        logger.info(
            {'msg': 'ingestion finished', 'path': options['path'],
             'records_ingested': records_ingested_count,
             'files_processed': files_processed})

    def iter_files_to_process(self, path: str) -> Iterator[Path]:
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

    def iter_rows_to_process(self, filepath_to_load: Path):
        with open(str(filepath_to_load), 'r') as f:
            for line in f:
                yield re.findall(r'\S+', line)
