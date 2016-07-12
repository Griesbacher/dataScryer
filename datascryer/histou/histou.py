import json
import logging

import jsonschema

import datascryer
from datascryer.helper.http import get
from datascryer.helper.python import python_3


class Histou:
    def __init__(self, protocol, address):
        self.protocol = protocol
        self.address = address
        self.schema = self.get_json_schema()

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
        "pattern": "^[0-9]+[smhw]$"
      },
      "forecast_range": {
        "type": "string",
        "description": "Time to predict",
        "pattern": "^[0-9]+[smhw]$"
      },
      "forecast_interval": {
        "type": "string",
        "description": "Time between predicted points.",
        "pattern": "^[0-9]+[smhw]$"
      },
      "update_rate": {
        "type": "string",
        "description": "Time between calculations.",
        "pattern": "^[0-9]+[smhw]$"
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
