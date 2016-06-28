import json
import logging
import os
import subprocess

import jsonschema

from datascryer.config import Config
from datascryer.helper.python import python_3

if python_3():
    import urllib.request
    import urllib.error
    import urllib.parse
else:
    import urllib2


class Histou:
    def __init__(self, protocol, address):
        self.protocol = protocol
        self.address = address
        with open(Config.data['main']['schema']) as json_schema:
            self.schema = json.load(json_schema)

    def get_config(self, host, service, command, perf_labels):
        if self.protocol == "http":
            url = self.address + "?host=%s&service=%s&command=%s"
            if python_3():
                url = _gen_url(url, host, service, command, perf_labels, urllib.parse.quote)
                response = urllib.request.urlopen(urllib.request.Request(url))

            else:
                url = _gen_url(url, host, service, command, perf_labels, urllib2.quote)
                response = urllib2.urlopen(urllib2.Request(url))

            if response.code != 200:
                Exception("Returncode is not 200: " + response.code)

            out = response.read()
        elif self.protocol == "file":
            current_dir = os.path.dirname(os.path.realpath(os.getcwd()))
            folder = os.path.split(self.address)[0:-1][0]
            cmd = ["php", os.path.basename(self.address),
                   "--host=" + host,
                   "--service=" + service,
                   "--command=" + command]
            for p in perf_labels:
                cmd.append("--perf_label=" + p)
            os.chdir(folder)
            out = subprocess.check_output(cmd)
            os.chdir(current_dir)
        else:
            logging.getLogger(__name__).error("Undefined Protocol: " + self.protocol)
            return None
        json_object = json.loads(out.decode('utf8'))
        try:
            jsonschema.validate(json_object, self.schema)
        except jsonschema.exceptions.ValidationError as e:
            logging.getLogger(__name__).error("JSON Config received from Histou is not valid: " + str(e))
            return None
        return json_object


def _gen_url(url, host, service, command, perf_labels, url_quote):
    url = url % (url_quote(host), url_quote(service), url_quote(command))
    for p in perf_labels:
        url += "&perf_label[]=" + url_quote(p)
    return url
