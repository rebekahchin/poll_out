# Sensor output values
## Location: Subang Jaya, Selangor, Malaysia
Output from the following sensors would be pushed to output.json.\
Comparison to official AQI statistics in progress.\
The sensors are:\
Temperature and humidity: HTU21D\
UV sensor: GUVA S12SD (with ADC converter: ADS1115)\
PM2.5 and PM10 sensor: PMS7003.\
Data in output.json:\
1. Date and time when measurement were taken.
2. PM 2.5 in ug / m^3
3. PM 10 in ug / m^3
4. UV index[^1]
5. AQI[^2]

[^1]: These values are not accurate and should not be used for quantitative analyses.
[^2]: Calculated using 24 hour average PM2.5 and PM 10 concentration. [Source](https://en.wikipedia.org/wiki/Air_quality_index#Computing_the_AQI)
