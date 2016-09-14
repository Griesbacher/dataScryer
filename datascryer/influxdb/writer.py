import logging

import datascryer.helper.http
from datascryer.helper.python import python_3
from datascryer.influxdb.connection import gen_url, gen_clean_url

if python_3():
    from io import StringIO
    from urllib.error import URLError
else:
    from cStringIO import StringIO
    from urllib2 import URLError


class InfluxDBWriter:
    def __init__(self, address, db_forecast, db_anomaly, args):
        InfluxDBWriter.url_forecast = gen_url(address, db_forecast, args, "write")
        InfluxDBWriter.url_anomaly = gen_url(address, db_anomaly, args, "write")
        self.url_query = gen_clean_url(address, "query")
        try:
            self.create_database(db_forecast)
            self.create_database(db_anomaly)
        except URLError as e:
            logging.getLogger(__name__).error("Could not create database or connect to influxdb: " + str(e))
            raise ConnectionError

    @staticmethod
    def write_forecast(data, host, service, performance_label, command=None):
        InfluxDBWriter._write(data, InfluxDBWriter.url_forecast, host, service, performance_label, command)

    @staticmethod
    def write_anomaly(data, host, service, performance_label, command=None):
        InfluxDBWriter._write(data, InfluxDBWriter.url_anomaly, host, service, performance_label, command)

    @staticmethod
    def _write(data, url, host, service, performance_label, command=None):
        line_data = StringIO()
        b = None
        for line in data:
            line_data.write('metrics,host=')
            line_data.write(host)
            line_data.write(',service=')
            line_data.write(service)
            if command:
                line_data.write(',command=')
                line_data.write(command)
            line_data.write(',performanceLabel=')
            line_data.write(performance_label)
            line_data.write(' value=')
            line_data.write("%.15f" % line[1])
            line_data.write(' ')
            line_data.write("%d" % line[0])
            line_data.write("\n")
        try:
            b = line_data.getvalue().encode('utf-8')
            datascryer.helper.http.post(url, b)
        except Exception as e:
            logging.getLogger(__name__).warn(e)
            logging.getLogger(__name__).warn(url)
            if b:
                logging.getLogger(__name__).warn(b)

    def create_database(self, db):
        datascryer.helper.http.post(
            self.url_query,
            "q=" + datascryer.helper.http.quote("CREATE DATABASE " + db)
        )
