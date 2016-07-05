import json
import logging

import jsonschema

import datascryer
from datascryer.config import Config
from datascryer.helper.http import get
from datascryer.helper.python import python_3


class Histou:
    def __init__(self, protocol, address):
        self.protocol = protocol
        self.address = address
        with open(Config.data['main']['schema']) as json_schema:
            self.schema = json.load(json_schema)

    def get_config(self, hosts_services):
        if self.protocol == "http":
            json_config = json.dumps(hosts_services)
            response = datascryer.helper.http.post(self.address, json_config, json=True)

            if response.code != 200:
                Exception("Returncode is not 200: " + response.code)

            out = response.read()
        else:
            logging.getLogger(__name__).error("Undefined Protocol: " + self.protocol)
            return None
        json_object = json.loads(out.decode('utf8'))
        for o in json_object:
            if o:
                try:
                    jsonschema.validate(o, self.schema)
                except jsonschema.exceptions.ValidationError as e:
                    logging.getLogger(__name__).error("JSON Config received from Histou is not valid: " + str(e),
                                                      exc_info=True)
        return json_object


def _gen_url(url, host, service, command, perf_labels, url_quote):
    url = url % (url_quote(host), url_quote(service), url_quote(command))
    for p in perf_labels:
        url += "&perf_label[]=" + url_quote(p)
    return url
