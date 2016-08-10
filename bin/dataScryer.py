#!/usr/bin/env python

import argparse
import logging
import sys

from datascryer.config import Config
from datascryer.influxdb.reader import InfluxDBReader
from datascryer.influxdb.writer import InfluxDBWriter
from datascryer.methods.method_collector import MethodCollector
from datascryer.mode.check import check_mode
from datascryer.mode.drawing import forecast_mode


def get_version():
    return "0.0.1"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Makes forecasts based on performancedata')
    parser.add_argument("--version", action='version', version=get_version())
    required = parser.add_argument_group('required arguments')
    required.add_argument("-c", "--config", help="Path to the config file", required=True)
    check = parser.add_argument_group('CheckMode arguments')
    check.add_argument("--check", help="Runs in check mode", action='store_true')
    check.add_argument("-H", "--host", help="Hostname")
    check.add_argument("-S", "--service", help="Servicename")
    check.add_argument("-C", "--command", help="Commandename")
    check.add_argument("-P", "--performanceLabel", help="PerformanceLabel")
    check.add_argument("-M", "--method", help="Method to calc check")
    check.add_argument("-L", "--lookback_range",
                       help="Timebase to calc check [Format: Tx : T=Float x=[ms|s|m|h|d|w]]")
    check.add_argument("-R", "--forecast_range",
                       help="Range to look in the future to calc check [Format: Tx : T=Float x=[ms|s|m|h|d]]")
    check.add_argument("-I", "--forecast_interval",
                       help="Intervall between calculations to calc check [Format: Tx : T=Float x=[ms|s|m|h|d]]")
    check.add_argument("-V", "--value", help="Y Value to reach", type=float)
    check.add_argument("-U", "--unit", help="Unit to return data[ms|s|m|h|d] default: s", default="s")
    check.add_argument("--warn", help="Warning X Value based on value", type=float)
    check.add_argument("--crit", help="Critical Y Value based on value", type=float)

    args = parser.parse_args()

    Config(args.config)

    logging.basicConfig(
        stream=sys.stdout,
        level=Config.data['main']['log_level'],
        format='%(asctime)s %(name)-40s %(levelname)-8s %(message)s',
        datefmt='%d-%m-%S %H:%M',
    )
    logging.captureWarnings(True)

    MethodCollector([Config.data['main']['customMethods']])

    InfluxDBReader(address=Config.data['influxdb']['read']['address'],
                   db=Config.data['influxdb']['read']['db'],
                   args=Config.data['influxdb']['read']['args']
                   )
    InfluxDBWriter(address=Config.data['influxdb']['write']['address'],
                   db=Config.data['influxdb']['write']['db'],
                   args=Config.data['influxdb']['write']['args'])

    if args.check:
        check_mode(args=args)
    else:
        forecast_mode()
