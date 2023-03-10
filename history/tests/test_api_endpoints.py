import pytest as pytest
from django.core.management import call_command


@pytest.mark.django_db
class TestAPIEndpoints:

    def setup_method(self, method):
        call_command('ingest_history',
                     'history/tests/files_for_testing/directory')

    class TestWeatherDayListView:

        def test_pagination_works(self, client):
            response1 = client.get('/api/weather/?limit=2')
            response2 = client.get('/api/weather/?limit=2&offset=2')
            response3 = client.get('/api/weather/?limit=2&offset=4')
            response4 = client.get('/api/weather/?limit=2&offset=6')

            assert response1.data['count'] == 6
            assert len(response1.data['results']) == 2
            assert response1.data['results'][0] == {
                'station': {
                    'code': 'file_to_load'
                },
                'date': '1989-03-13',
                'temperature_max': 122,
                'temperature_min': -44,
                'precipitation': None
            }
            assert response1.data['results'][1] == {
                'station': {
                    'code': 'file_to_load'
                },
                'date': '1989-03-14',
                'temperature_max': 189,
                'temperature_min': None,
                'precipitation': 53
            }

            assert response2.data['count'] == 6
            assert len(response2.data['results']) == 2
            assert response2.data['results'][0] == {
                'station': {
                    'code': 'file_to_load'
                },
                'date': '1989-03-15',
                'temperature_max': None,
                'temperature_min': 6,
                'precipitation': 0
            }
            assert response2.data['results'][1] == {
                'station': {
                    'code': 'file_to_load'
                },
                'date': '1989-03-16',
                'temperature_max': 94,
                'temperature_min': -33,
                'precipitation': 0
            }

            assert response3.data['count'] == 6
            assert len(response3.data['results']) == 2
            assert response3.data['results'][0] == {
                'station': {
                    'code': 'file_to_load2'
                },
                'date': '1989-03-13',
                'temperature_max': 122,
                'temperature_min': -44,
                'precipitation': None
            }
            assert response3.data['results'][1] == {
                'station': {
                    'code': 'file_to_load2'
                },
                'date': '1989-03-14',
                'temperature_max': 189,
                'temperature_min': None,
                'precipitation': 53
            }

            assert response4.data['count'] == 6
            assert len(response4.data['results']) == 0

        def test_station_filter_works(self, client):
            response = client.get('/api/weather/?station__code=file_to_load2')

            assert response.data['count'] == 2
            assert response.data['results'][0] == {
                'station': {
                    'code': 'file_to_load2'
                },
                'date': '1989-03-13',
                'temperature_max': 122,
                'temperature_min': -44,
                'precipitation': None
            }
            assert response.data['results'][1] == {
                'station': {
                    'code': 'file_to_load2'
                },
                'date': '1989-03-14',
                'temperature_max': 189,
                'temperature_min': None,
                'precipitation': 53
            }

        def test_date_filter_works(self, client):
            response = client.get('/api/weather/?date=1989-03-13')

            assert response.data['count'] == 2
            assert response.data['results'][0] == {
                'station': {
                    'code': 'file_to_load'
                },
                'date': '1989-03-13',
                'temperature_max': 122,
                'temperature_min': -44,
                'precipitation': None
            }
            assert response.data['results'][1] == {
                'station': {
                    'code': 'file_to_load2'
                },
                'date': '1989-03-13',
                'temperature_max': 122,
                'temperature_min': -44,
                'precipitation': None
            }

        def test_pagination_and_filters_work_together(self, client):
            response = client.get(
                '/api/weather/?limit=2&offset=2&station__code=file_to_load')

            assert response.data['count'] == 4
            assert response.data['results'][0] == {
                'station': {
                    'code': 'file_to_load'
                },
                'date': '1989-03-15',
                'temperature_max': None,
                'temperature_min': 6,
                'precipitation': 0
            }
            assert response.data['results'][1] == {
                'station': {
                    'code': 'file_to_load'
                },
                'date': '1989-03-16',
                'temperature_max': 94,
                'temperature_min': -33,
                'precipitation': 0
            }

    class TestWeatherStatsListView:

        def test_pagination_works(self, client):
            response = client.get('/api/weather/stats?limit=1&offset=1')

            assert response.data['count'] == 2
            assert len(response.data['results']) == 1
            assert response.data['results'][0] == {
                'station': {
                    'code': 'file_to_load2'
                },
                'year': 1989,
                'avg_temperature_max': '15.55',
                'avg_temperature_min': '-4.40',
                'total_precipitation': '0.53'
            }

        def test_station_filter_works(self, client):
            response = client.get(
                '/api/weather/stats?station__code=file_to_load2')

            assert response.data['count'] == 1
            assert response.data['results'][0] == {
                'station': {
                    'code': 'file_to_load2'
                },
                'year': 1989,
                'avg_temperature_max': '15.55',
                'avg_temperature_min': '-4.40',
                'total_precipitation': '0.53'
            }

        def test_year_filter_works(self, client):
            response1 = client.get('/api/weather/stats?year=1989')
            response2 = client.get('/api/weather/stats?year=1990')

            assert response1.data['count'] == 2
            assert response2.data['count'] == 0

        def test_pagination_and_filters_work_together(self, client):
            response = client.get(
                '/api/weather/stats?station__code=file_to_load2&year=1989')

            assert response.data['count'] == 1
