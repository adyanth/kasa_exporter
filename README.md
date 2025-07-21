# Kasa Smart Plug (Energy Monitoring) exporter

The exporter expects the following env vars for operation with newer Kasa/Tapo devices: `KASA_USERNAME`, `KASA_PASSWORD`.
This is your TP-Link Kasa email and password.

A comma separated list of IP addresses can be passed in with `KASA_PLUGS`. This will disable auto discovery. Helpful for when a broadcast does not work for discovery (e.g. from a different subnet).

An optional `SCRAPE_SLEEP_INTERVAL` can be set (defaults to `5` seconds) to set how long to sleep between scrapes.

An optional `PROMETHEUS_PORT` can be set (defaults to `8000`)
