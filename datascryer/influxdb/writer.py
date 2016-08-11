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
    url = None

    def __init__(self, address, db, args):
        InfluxDBWriter.db = db
        InfluxDBWriter.url = gen_url(address, db, args, "write")
        InfluxDBWriter.url_query = gen_clean_url(address, "query")
        try:
            self.create_database()
        except URLError as e:
            logging.getLogger(__name__).error("Could not create database or connect to influxdb: " + str(e))
            raise ConnectionError

    @staticmethod
    def write(data, host, service, performance_label, command=None):
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
            datascryer.helper.http.post(InfluxDBWriter.url, b)
        except Exception as e:
            logging.getLogger(__name__).warn(e)
            logging.getLogger(__name__).warn(InfluxDBWriter.url)
            if b:
                logging.getLogger(__name__).warn(b)

    @staticmethod
    def create_database():
        datascryer.helper.http.post(
            InfluxDBWriter.url_query,
            "q=" + datascryer.helper.http.quote("CREATE DATABASE " + InfluxDBWriter.db)
        )
