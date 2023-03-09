from rest_framework import serializers

from history.models import WeatherDay, WeatherStats, WeatherStation


class WeatherStationSerializer(serializers.ModelSerializer):

    class Meta:
        model = WeatherStation
        fields = ('code', )


class WeatherDaySerializer(serializers.ModelSerializer):

    class Meta:
        model = WeatherDay
        fields = ('station', 'date', 'temperature_max', 'temperature_min',
                  'precipitation')

    station = WeatherStationSerializer()


class WeatherStatsSerializer(serializers.ModelSerializer):

    class Meta:
        model = WeatherStats
        fields = ('station', 'year', 'avg_temperature_max',
                  'avg_temperature_min', 'total_precipitation')

    station = WeatherStationSerializer()
