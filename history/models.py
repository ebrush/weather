from django.db import models


class WeatherStation(models.Model):
    name = models.CharField(blank=False, max_length=20, unique=True)


class WeatherDay(models.Model):
    station = models.ForeignKey(
        WeatherStation, null=False, on_delete=models.CASCADE)
    date = models.DateField(null=False)
    temperature_max = models.SmallIntegerField(
        null=True, help_text='in tenths of a degree Celsius')
    temperature_min = models.SmallIntegerField(
        null=True, help_text='in tenths of a degree Celsius')
    precipitation = models.PositiveSmallIntegerField(
        null=True, help_text='in tenths of a millimeter')

    class Meta:
        unique_together = ('station', 'date')


class WeatherStats(models.Model):
    station = models.ForeignKey(
        WeatherStation, null=False, on_delete=models.CASCADE)
    year = models.PositiveSmallIntegerField(null=False)
    avg_temperature_max = models.SmallIntegerField(
        null=True, help_text='in degrees Celsius')
    avg_temperature_min = models.SmallIntegerField(
        null=True, help_text='in degrees Celsius')
    total_precipitation = models.PositiveSmallIntegerField(
        null=True, help_text='in centimeters')

    class Meta:
        unique_together = ('station', 'year')
