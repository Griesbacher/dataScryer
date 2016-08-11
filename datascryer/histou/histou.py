import json
import logging
import os
import subprocess

import jsonschema
import requests

from datascryer.config import Config
from datascryer.helper.python import python_3

if python_3():
    from urllib.error import URLError
else:
    from urllib2 import URLError


class Histou:
    POST_HEADER = {
        'User-Agent': "It's me, wget!",
        "Content-Type": "application/json"
    }

    def __init__(self, protocol, address):
        self.protocol = protocol
        self.address = address
        self.schema = json.loads(self.get_json_schema())
        # Disable SSL verification warning
        requests.packages.urllib3.disable_warnings()

    def get_config(self, hosts_services):
        json_config = json.dumps(hosts_services)
        if self.protocol == "http":
            r = requests.post(url=self.address, data=json_config,
                              auth=(Config.data['histou']['user'], Config.data['histou']['password']),
                              verify=False, headers=Histou.POST_HEADER)
            if r.status_code != 200:
                raise URLError("Returncode is not 200: " + str(r.status_code))

            out = r.text
        elif self.protocol == "file":
            current_dir = os.path.dirname(os.path.realpath(os.getcwd()))
            folder = os.path.split(self.address)[0:-1][0]
            cmd = ["php", os.path.basename(self.address), "--request=" + json_config]
            os.chdir(folder)
            out = subprocess.check_output(cmd).decode('utf8')
            os.chdir(current_dir)
        else:
            logging.getLogger(__name__).error("Undefined Protocol: " + self.protocol)
            return None
        json_object = json.loads(out)
        for o in json_object:
            if o:
                try:
                    jsonschema.validate(o, self.schema)
                except jsonschema.exceptions.ValidationError as e:
                    logging.getLogger(__name__).error("JSON Config received from Histou is not valid: " + str(e),
                                                      exc_info=True)
        return json_object

    @staticmethod
    def get_json_schema():
        return """
{
  "$schema": "http://json-schema.org/draft-04/schema#",
  "type": "array",
  "items": {
    "type": "object",
    "properties": {
      "label": {
        "type": "string",
        "description": "Performancelabel"
      },
      "method": {
        "type": "string",
        "description": "Method to calc forecast"
      },
      "methodSpecificOptions": {
      },
      "lookback_range": {
        "type": "string",
        "description": "Timebase for forecast",
        "pattern": "^[0-9]+[smhd]$"
      },
      "forecast_range": {
        "type": "string",
        "description": "Time to predict",
        "pattern": "^[0-9]+[smhd]$"
      },
      "forecast_interval": {
        "type": "string",
        "description": "Time between predicted points.",
        "pattern": "^[0-9]+[smhd]$"
      },
      "update_rate": {
        "type": "string",
        "description": "Time between calculations.",
        "pattern": "^[0-9]+[smhd]$"
      }
    },
    "required": [
      "label",
      "method",
      "methodSpecificOptions",
      "lookback_range",
      "forecast_range",
      "forecast_interval",
      "update_rate"
    ]
  }
}
"""
