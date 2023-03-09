from django.db import models


class WeatherStation(models.Model):
    """represents a weather station."""
    code = models.CharField(blank=False, max_length=20, unique=True,
                            help_text='indicates file/station '
                                      'weather data came from')

    def __str__(self):
        return f'Station({self.code})'


class WeatherDay(models.Model):
    """one day of weather info for one station"""
    station = models.ForeignKey(
        WeatherStation, null=False, on_delete=models.CASCADE, db_index=True)
    date = models.DateField(null=False, db_index=True)
    temperature_max = models.SmallIntegerField(
        null=True, help_text='in tenths of a degree Celsius')
    temperature_min = models.SmallIntegerField(
        null=True, help_text='in tenths of a degree Celsius')
    precipitation = models.PositiveSmallIntegerField(
        null=True, help_text='in tenths of a millimeter')

    class Meta:
        unique_together = ('station', 'date')
        ordering = ('station__code', 'date')

    def __str__(self):
        return f'WeatherDay(station={self.station.code}, date={self.date})'


class WeatherStats(models.Model):
    """statistics for a year of weather for one station"""
    station = models.ForeignKey(
        WeatherStation, null=False, on_delete=models.CASCADE, db_index=True)
    year = models.PositiveSmallIntegerField(null=False, db_index=True)
    avg_temperature_max = models.DecimalField(
        null=True, help_text='in degrees Celsius',
        max_digits=6, decimal_places=2)
    avg_temperature_min = models.DecimalField(
        null=True, help_text='in degrees Celsius',
        max_digits=6, decimal_places=2)
    total_precipitation = models.DecimalField(  # max_digits value determined by looking at max found within the files and a Google search of weather history, then adding a couple extra digits
        null=True, help_text='in centimeters',
        max_digits=7, decimal_places=2)

    class Meta:
        unique_together = ('station', 'year')
        ordering = ('station__code', 'year')

    def __str__(self):
        return f'WeatherStats(station={self.station.code}, year={self.year})'
