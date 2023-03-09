from pathlib import Path

from django.core.management import call_command, CommandError
import pytest

from history.management.commands.ingest_history import Command

from history.models import WeatherStation


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


class TestIterFilesToProcess:
    def test_no_rows_to_process_when_arg_is_empty_file(self):
        assert list(Command().iter_rows_to_process(
            Path('history/tests/files_for_testing/EMPTYFILE0.txt'))) == []

    def test_every_row_when_arg_has_rows(self):
        assert list(Command().iter_rows_to_process(
            'history/tests/files_for_testing/directory/file_to_load.txt')) == [
                   ['19890313', '122', '-44', '0'],
                   ['19890314', '189', '17', '53'],
                   ['19890315', '-9999', '6', '0'],
                   ['19890316', '94', '-33', '0'],
               ]
