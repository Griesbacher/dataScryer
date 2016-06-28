import json
import logging

import datascryer
from datascryer.helper.http import quote, get
from datascryer.helper.python import python_3
from datascryer.influxdb.connection import gen_url

if python_3():
    pass
else:
    pass


class InfluxDBReader:
    url = None

    def __init__(self, address, db, args):
        InfluxDBReader.url = gen_url(address, db, args, "query")
        if not str.endswith(InfluxDBReader.url, "&"):
            InfluxDBReader.url += "&"
        InfluxDBReader.url += "q="

    @staticmethod
    def request_past(host, service, performance_label, lookback, command=None):
        if not command:
            query = """SELECT value FROM metrics WHERE host = '%s' AND service = '%s' AND performanceLabel = '%s' AND time > now() - %dms""" % (
                host, service, performance_label, lookback)
        else:
            query = """SELECT value FROM metrics WHERE host = '%s' AND service = '%s' AND command = '%s' AND performanceLabel = '%s' AND time > now() - %dms""" % (
                host, service, command, performance_label, lookback)
        url = InfluxDBReader.url + quote(query)
        response = get(url)
        json_object = json.loads(datascryer.helper.http.read(response))

        if ('results' not in json_object or
                    len(json_object['results']) == 0 or
                    'series' not in json_object['results'][0] or
                    len(json_object['results'][0]['series']) == 0 or
                    'columns' not in json_object['results'][0]['series'][0] or
                    len(json_object['results'][0]['series'][0]['columns']) < 2):
            logging.getLogger(__name__).warn("InfluxDB query did not return proper results: " + query)
            logging.getLogger(__name__).warn(url + " --> " + str(json_object))
            return None

        if "time" not in json_object['results'][0]['series'][0]['columns'] or "value" not in \
                json_object['results'][0]['series'][0]['columns']:
            logging.getLogger(__name__).warn(
                "Neither time nor value is in columns: " + query + "\n" +
                json_object['results'][0]['series'][0]['columns']
            )

        if (json_object['results'][0]['series'][0]['columns'][0] == "time" and
                    json_object['results'][0]['series'][0]['columns'][1] == "value"):
            return json_object['results'][0]['series'][0]['values']
        else:
            logging.getLogger(__name__).warn("Columns are flipped")
