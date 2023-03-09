from rest_framework.generics import ListAPIView

from history.models import WeatherDay, WeatherStats
from history.serializers import WeatherDaySerializer, WeatherStatsSerializer


class WeatherDayListView(ListAPIView):
    """Lists information on a day of weather by station"""

    queryset = WeatherDay.objects.all()
    serializer_class = WeatherDaySerializer
    filterset_fields = ('station__code', 'date')


class WeatherStatsListView(ListAPIView):
    """Lists statistical information on a year of weather by station"""

    queryset = WeatherStats.objects.all()
    serializer_class = WeatherStatsSerializer
    filterset_fields = ('station__code', 'year')
