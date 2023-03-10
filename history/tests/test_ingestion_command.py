from pathlib import Path

from django.core.management import call_command, CommandError
import pytest

from history.management.commands.ingest_history import Command

from history.models import WeatherStation, WeatherDay, WeatherStats


class TestIngestHistoryCommandCalls:
    def test_requires_path(self):
        with pytest.raises(CommandError) as e:
            call_command('ingest_history')

        assert 'arguments are required: path' in str(e)

    def test_handles_nonexistent_file(self):
        with pytest.raises(CommandError) as e:
            call_command('ingest_history',
                         'history/tests/files_for_testing/nonexistent.txt')

        assert 'provided path does not exist' in str(e)

    def test_handles_empty_file_and_station_created(self, db):
        call_command('ingest_history',
                     'history/tests/files_for_testing/EMPTYFILE0.txt')

        assert WeatherStation.objects.filter(code='EMPTYFILE0').exists()

    def test_correct_values_and_statistics_stored_and_duplicates_overwritten(
            self, db):
        call_command('ingest_history',
                     'history/tests/files_for_testing/directory/file_to_load2.txt')

        assert WeatherDay.objects.count() == 2
        assert WeatherDay.objects.filter(
            station__code='file_to_load2',
            date__year=1989,
            date__month=3,
            date__day=13,
            temperature_max=122,
            temperature_min=-44,
            precipitation=None,
        ).exists()
        assert WeatherDay.objects.filter(
            station__code='file_to_load2',
            date__year=1989,
            date__month=3,
            date__day=14,
            temperature_max=189,
            temperature_min=None,
            precipitation=53,
        ).exists()
        assert WeatherStats.objects.count() == 1
        assert WeatherStats.objects.filter(
            station__code='file_to_load2',
            year=1989,
            avg_temperature_max=15.55,
            avg_temperature_min=-4.40,
            total_precipitation=.53,
        ).exists()


class TestIterFilesToProcess:
    def test_one_file_to_process_when_arg_is_file(self):
        assert list(Command().iter_files_to_process(
            'history/tests/files_for_testing/EMPTYFILE0.txt')) == [
                   Path('history/tests/files_for_testing/EMPTYFILE0.txt'),
               ]

    def test_all_files_to_process_when_arg_is_directory(self):
        assert list(Command().iter_files_to_process(
            'history/tests/files_for_testing/directory')) == [
                   Path(
                       'history/tests/files_for_testing/directory/file_to_load.txt'),
                   Path(
                       'history/tests/files_for_testing/directory/file_to_load2.txt'),
               ]


class TestIterRowsToProcess:
    def test_no_rows_to_process_when_arg_is_empty_file(self):
        assert list(Command().iter_rows_to_process(
            'history/tests/files_for_testing/EMPTYFILE0.txt')) == []

    def test_every_row_with_missing_vals_as_null_when_arg_has_rows(self):
        assert list(Command().iter_rows_to_process(
            'history/tests/files_for_testing/directory/file_to_load.txt')) == [
                   ['19890313', '122', '-44', None],
                   ['19890314', '189', None, '53'],
                   ['19890315', None, '6', '0'],
                   ['19890316', '94', '-33', '0'],
               ]
