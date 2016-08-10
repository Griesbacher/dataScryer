from datascryer.helper.time_converter import string_to_ms, Units
from datascryer.influxdb.reader import InfluxDBReader
from datascryer.jobs.job import Job
from datascryer.methods.abc_forecast import ForecastMethod
from datascryer.methods.method_collector import MethodCollector
from datascryer.mode.returncodes import Returncodes


def check_mode(args):
    Units
    required = ["command", "forecast_interval", "forecast_range", "host", "lookback_range", "method",
                "performanceLabel", "service", "value"]
    for r in required:
        if eval("args." + r) is None:
            plugin_exit(Returncodes.Unknown, r + " can not be empty in CheckMode")

    method = args.method.lower()
    if method not in MethodCollector.classes.keys():
        plugin_exit(Returncodes.Unknown, "Method " + method + "is unknown")

    forecast_interval = string_to_ms(args.forecast_interval)
    forecast_range = string_to_ms(args.forecast_range)
    lookback_range = string_to_ms(args.lookback_range)
    lookback_data = InfluxDBReader.request_past(host=args.host,
                                                service=args.service,
                                                performance_label=args.performanceLabel,
                                                lookback=lookback_range)
    if not lookback_data:
        plugin_exit(Returncodes.Unknown, "Could not fetch data from InfluxDB")
    result = MethodCollector.classes[method]. \
        calc_intersection(
        # TODO: if needed add args
        options={},
        forecast_start=Job.calc_start_date(
            lookback_data[len(lookback_data) - 1][0],
            forecast_interval),
        forecast_range=forecast_range,
        forecast_interval=forecast_interval,
        lookback_range=lookback_range,
        lookback_data=lookback_data,
        y=args.value)

    casted_result = None
    try:
        casted_result = result / eval("Units." + args.unit)
    except AttributeError:
        plugin_exit(Returncodes.Unknown, "Unit: " + args.unit + " is unknown")

    if args.warn and args.warn < casted_result:
        plugin_exit(Returncodes.Warning, "Reached in: " + str(casted_result) + args.unit,
                    casted_result, args.unit, args.warn, args.crit)
    elif args.crit and args.crit < casted_result:
        plugin_exit(Returncodes.Critical, "Reached in: " + str(casted_result) + args.unit,
                    casted_result, args.unit, args.warn, args.crit)
    else:
        plugin_exit(Returncodes.OK, "Reached in: " + str(casted_result) + " " + args.unit + " ",
                    casted_result, args.unit, args.warn, args.crit)


def plugin_exit(state, message, perf_value="", unit="", perf_warn="", perf_crit=""):
    out = "Forecast " + Returncodes.name(state) + ": " + message
    if perf_value:
        if perf_value == ForecastMethod.INF:
            perf_value = -1
        out += "|'reached'=" + str(perf_value) + unit + ";"
        if perf_warn:
            out += str(perf_warn)
        out += ";"
        if perf_crit:
            out += str(perf_crit)
    print(out)
    exit(state)
