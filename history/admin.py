from django.contrib import admin

from history.models import WeatherDay, WeatherStation, WeatherStats

admin.site.register(WeatherDay)
admin.site.register(WeatherStation)
admin.site.register(WeatherStats)
