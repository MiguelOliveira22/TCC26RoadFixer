# Exemplo de retorno do site open-meteo

```json
[
    {
        "latitude": -22.90,
        "longitude": -47.05,
        "timezone": "America/Sao_Paulo",
        "hourly_units": {
        "time": "iso8601",
        "precipitation": "mm",
        "wind_speed_10m": "km/h"
        },
        "hourly": {
        "time": ["2024-01-08T00:00", "2024-01-08T01:00", "..."],
        "precipitation": [0.0, 0.0, 12.5, "..."],
        "rain": [0.0, 0.0, 12.5, "..."],
        "temperature_2m": [22.1, 21.8, 20.4, "..."],
        "weather_code": [0, 0, 61, "..."],
        "wind_speed_10m": [10.2, 11.5, 25.0, "..."],
        "wind_gusts_10m": [15.0, 18.2, 45.1, "..."]
        }
    },
    {
        "latitude": -22.95,
        "longitude": -47.09,
        "...": "Mesma estrutura para o Ponto B"
    },
    {
        "latitude": -22.99,
        "longitude": -47.12,
        "...": "Mesma estrutura para o Ponto C"
    }
]
```