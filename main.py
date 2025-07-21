#!/usr/bin/env python3

import asyncio
from kasa import Device, DeviceType, Discover
from kasa.module import Module
from os import environ
from prometheus_client import Gauge, start_http_server
from time import sleep

from dotenv import load_dotenv
load_dotenv()

KASA_USERNAME = environ.get("KASA_USERNAME")
KASA_PASSWORD = environ.get("KASA_PASSWORD")
SCRAPE_SLEEP_INTERVAL = float(environ.get("SCRAPE_SLEEP_INTERVAL", "5"))
PROMETHEUS_PORT = int(environ.get("PROMETHEUS_PORT", "8000"))
KASA_PLUGS = environ.get("KASA_PLUGS", "").split(",")

async def scrape_ip(
        dev: Device,
        p_gauge: Gauge,
        v_gauge: Gauge,
        i_gauge: Gauge,
        today_counter: Gauge,
        this_month_counter: Gauge
    ):
    try:
        await dev.update()
        energy = dev.modules[Module.Energy]
        p_gauge.labels(alias=dev.alias, model=dev.model).set(energy.status.power)
        v_gauge.labels(alias=dev.alias, model=dev.model).set(energy.status.voltage)
        i_gauge.labels(alias=dev.alias, model=dev.model).set(energy.status.current)
        today_counter.labels(alias=dev.alias, model=dev.model).set(energy.consumption_today)
        this_month_counter.labels(alias=dev.alias, model=dev.model).set(energy.consumption_this_month)
        # print(f"{energy.status=}")
        # print(f"{energy.consumption_today=}")
        # print(f"{energy.consumption_this_month=}")
        # if isinstance(energy, Emeter):
        #     print(f"{await energy.get_daily_stats()=}")
        #     print(f"{await energy.get_monthly_stats()=}")
        #     pass
        # elif isinstance(energy, Energy):
        #     print(f"{energy.energy=}")
    except:
        print(f"Failed to scrape {dev}")

def discover_handler_wrapper():
    plugs = []
    async def discover_handler(dev: Device):
        await dev.update()
        if dev.device_type == DeviceType.Plug and dev.has_emeter:
            plugs.append(dev)
            print(f"Discovered {dev.model}: {dev.alias}")
    return discover_handler, plugs

async def main():
    print("Running main")

    p_gauge = Gauge("plug_power_watts", "Current power consumed in Watts", ["alias", "model"])
    v_gauge = Gauge("plug_voltage_volts", "Current plug voltage in Volts", ["alias", "model"])
    i_gauge = Gauge("plug_current_amps", "Current current flow in Amps ", ["alias", "model"])
    today_counter = Gauge("plug_consumption_today_kwh", "Total energy consumption today in KWh", ["alias", "model"])
    this_month_counter = Gauge("plug_consumption_this_month_kwh", "Total energy consumtion this month in KWh", ["alias", "model"])

    handler, KASA_SMART_PLUGS = discover_handler_wrapper()
    if not KASA_PLUGS or not KASA_PLUGS[0]:
        await Discover.discover(
            on_discovered=handler,
            username=KASA_USERNAME,
            password=KASA_PASSWORD,
        )
    else:
        await asyncio.gather(
            *[
                handler(
                    await Discover.discover_single(
                        host=ip,
                        username=KASA_USERNAME,
                        password=KASA_PASSWORD,
                    )
                )
                for ip in KASA_PLUGS
            ]
        )

    if not KASA_SMART_PLUGS:
        raise Exception("No smart plugs found, try kasa discover")

    print("Running loop")
    while True:
        await asyncio.gather(
            *[
                scrape_ip(
                    dev,
                    p_gauge,
                    v_gauge,
                    i_gauge,
                    today_counter,
                    this_month_counter,
                )
                for dev in KASA_SMART_PLUGS
            ]
        )            
        sleep(SCRAPE_SLEEP_INTERVAL)

if __name__ == "__main__":
    start_http_server(PROMETHEUS_PORT)
    asyncio.run(main())
