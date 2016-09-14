import logging
import math
import threading
import time
from random import randint

from datascryer.config import log_peformance
from datascryer.helper.python import python_3, delta_ms
from datascryer.helper.time_converter import string_to_ms
from datascryer.influxdb.reader import InfluxDBReader
from datascryer.influxdb.writer import InfluxDBWriter
from datascryer.methods.method_collector import MethodCollector

if python_3():
    from urllib.error import URLError
else:
    from urllib2 import URLError

METHOD = 'method'
LABEL = 'label'
UPDATE_RATE = 'update_rate'
LOOKBACK_RANGE = 'lookback_range'
FORECAST_RANGE = 'forecast_range'
FORECAST_INTERVAL = 'forecast_interval'
METHOD_OPTIONS = 'methodSpecificOptions'

TIME_KEYS = [UPDATE_RATE, LOOKBACK_RANGE, FORECAST_RANGE, FORECAST_INTERVAL]


class Job(threading.Thread):
    def __init__(self, config):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.__stop_event = threading.Event()

        self.__host = config[0]
        self.__service = config[1]
        self.__command = config[2]['command']
        self.__config = config[2]
        self.__update_rates = []
        for p in self.__config['perf_labels']:
            for c in self.__config['config']:
                if p == c[LABEL]:
                    if self.get_method(c) in MethodCollector.classes.keys():
                        self.__update_rates.append((string_to_ms(c[UPDATE_RATE]), c))
                    else:
                        logging.warning("for " + c[METHOD] + " does no class exist")
        for u in self.__update_rates:
            for k, v in u[1].items():
                if k in TIME_KEYS:
                    u[1][k] = string_to_ms(v)
        self.__update_rates = sorted(self.__update_rates, key=lambda x: x[0])

    def stop(self):
        self.__stop_event.set()

    def run(self):
        if len(self.__update_rates) == 0:
            return

        # wait up to 120 seconds, to get some distortion
        self.__stop_event.wait(randint(0, 120))

        while not self.__stop_event.is_set():
            start = time.time()
            for update in self.__update_rates:
                rate = update[0]
                now = time.time()
                time_to_wait = round(start - now + rate / 1000, 0)
                interrupt = self.__stop_event.wait(time_to_wait)
                if interrupt:
                    return
                try:
                    self.start_calculation(update[1])
                except URLError as e:
                    logging.getLogger(__name__).error("Could not connect to InfluxDB: " + str(e))
                except:
                    logging.getLogger(__name__).error("Job execution failed", exc_info=True)

    def start_calculation(self, conf):
        start = time.time()
        lookback_data = InfluxDBReader.request_past(host=self.__host,
                                                    service=self.__service,
                                                    # command=self.__command,
                                                    performance_label=conf[LABEL],
                                                    lookback=conf[LOOKBACK_RANGE])
        if not lookback_data:
            return
        if log_peformance():
            logging.getLogger(__name__).debug(
                "Fetching data of %s %s %s: %s took %dms" % (
                    self.__host, self.__service, conf[LABEL], self.get_method(conf), delta_ms(start))
            )
        start = time.time()
        my_class = MethodCollector.classes[self.get_method(conf)]
        if 'calc_forecast' in dir(my_class):
            forecast_data = my_class. \
                calc_forecast(options=conf[METHOD_OPTIONS],
                              forecast_start=self.calc_start_date(lookback_data[len(lookback_data) - 1][0],
                                                                  conf[FORECAST_INTERVAL]),
                              forecast_range=conf[FORECAST_RANGE],
                              forecast_interval=conf[FORECAST_INTERVAL],
                              lookback_range=conf[LOOKBACK_RANGE],
                              lookback_data=lookback_data)
            if log_peformance():
                logging.getLogger(__name__).debug(
                    "Calculation data of %s %s %s: %s took %dms" % (
                        self.__host, self.__service, conf[LABEL], self.get_method(conf), delta_ms(start))
                )
            start = time.time()
            if forecast_data:
                InfluxDBWriter.write_forecast(data=forecast_data,
                                              host=self.__host,
                                              service=self.__service,
                                              # command=self.__command,
                                              performance_label=conf[LABEL])
                if log_peformance():
                    logging.getLogger(__name__).debug(
                        "Writing data of %s %s %s: %s took %dms" % (
                            self.__host, self.__service, conf[LABEL], self.get_method(conf), delta_ms(start))
                    )
            else:
                logging.getLogger(__name__).debug(
                    "Calculation did not return any data: %s %s %s: %s" % (
                        self.__host, self.__service, conf[LABEL], self.get_method(conf))
                )
        elif 'search_anomaly' in dir(my_class):
            anomaly_data = my_class.search_anomaly(
                options=conf[METHOD_OPTIONS],
                lookback_range=conf[LOOKBACK_RANGE],
                lookback_data=lookback_data)
            if log_peformance():
                logging.getLogger(__name__).debug(
                    "Calculation data of %s %s %s: %s took %dms" % (
                        self.__host, self.__service, conf[LABEL], self.get_method(conf), delta_ms(start))
                )
            if anomaly_data:
                InfluxDBWriter.write_anomaly(data=anomaly_data,
                                             host=self.__host,
                                             service=self.__service,
                                             # command=self.__command,
                                             performance_label=conf[LABEL])
                if log_peformance():
                    logging.getLogger(__name__).debug(
                        "Writing data of %s %s %s: %s took %dms" % (
                            self.__host, self.__service, conf[LABEL], self.get_method(conf), delta_ms(start))
                    )
            else:
                logging.getLogger(__name__).debug(
                    "Calculation did not return any data: %s %s %s: %s" % (
                        self.__host, self.__service, conf[LABEL], self.get_method(conf))
                )

    @staticmethod
    def get_method(c):
        if python_3():
            method_name = c[METHOD]
        else:
            method_name = c[METHOD].encode('utf8')
        return str.lower(method_name)

    @staticmethod
    def calc_start_date(last_data_point, interval):
        return math.ceil(float(last_data_point) / interval) * interval
