import csv
import datetime
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db.models import F, Sum, Avg

from history.models import WeatherDay, WeatherStation, WeatherStats


class Command(BaseCommand):
    help = 'Loads weather data from station files'

    def add_arguments(self, parser):
        parser.add_argument('filename', type=str,
                            help='Path to input file or directory '
                                 'containing files. Subdirectories '
                                 'will not be processed.')

    def handle(self, *args, **options):
        path = Path(options['filename'])
        if not path.exists():
            raise CommandError('provided filename does not exist')
        if path.is_dir():
            file_paths_to_load = path.iterdir()
        else:
            file_paths_to_load = [options['filename']]

        for filename_to_load in file_paths_to_load:
            path = Path(filename_to_load)
            if path.is_dir():
                print('skipping subdirectory', filename_to_load)
                continue

            station = WeatherStation.objects.get_or_create(
                defaults={'code': path.stem},
                code=path.stem
            )[0]
            years_updated = set()

            with open(filename_to_load, 'r') as f:
                reader = csv.reader(f, delimiter='\t')
                weather_days_to_create = []
                for (date, temperature_max,
                     temperature_min, precipitation) in reader:
                    date = datetime.datetime.strptime(date, '%Y%m%d').date()
                    years_updated.add(date.year)
                    weather_days_to_create.append(WeatherDay(
                        station=station,
                        date=date,
                        temperature_max=(temperature_max
                                         if temperature_max != '-9999'
                                         else None),
                        temperature_min=(temperature_min
                                         if temperature_min != '-9999'
                                         else None),
                        precipitation=(precipitation
                                       if precipitation != '-9999'
                                       else None),
                    ))
                WeatherDay.objects.bulk_create(
                    weather_days_to_create,
                    update_conflicts=True,
                    update_fields=('temperature_max', 'temperature_min',
                                   'precipitation'),
                    unique_fields=('station', 'date'),
                )

        stats_to_update = []
        for r in WeatherDay.objects.filter(station=station,
                                           date__year__in=years_updated).values(
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
