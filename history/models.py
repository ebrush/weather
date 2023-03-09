from django.db import models


class WeatherStation(models.Model):
    code = models.CharField(blank=False, max_length=20, unique=True)


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
        ordering = ('station__code', 'date')


class WeatherStats(models.Model):
    station = models.ForeignKey(
        WeatherStation, null=False, on_delete=models.CASCADE)
    year = models.PositiveSmallIntegerField(null=False)
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
