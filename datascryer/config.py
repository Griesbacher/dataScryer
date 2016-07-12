from distutils.util import strtobool

from datascryer.helper.python import python_3

if python_3():
    import configparser
else:
    import ConfigParser


class ConfigfileException(Exception):
    pass


class Config:
    data = dict()

    def __init__(self, file):
        if python_3():
            self.__settings = configparser.ConfigParser()
        else:
            self.__settings = ConfigParser.SafeConfigParser()
        try:
            with open(file) as f:
                self.__settings.readfp(f)
        except IOError as e:
            raise ConfigfileException(e)

        # Main
        self.data['main'] = {'customMethods': self.__settings.get('Main', 'Custom_Methods'),
                             'log_level': self.__settings.get('Main', 'Log_Level'),
                             'daemon': strtobool(self.__settings.get('Main', 'Daemon')),
                             'update_rate': int(self.__settings.get('Main', 'Config_Updaterate_in_Minutes')) * 60,
                             'log_performance': strtobool(self.__settings.get('Main', 'Log_Performance'))}

        # Livestatus
        livestatus_split = self.__settings.get('Livestatus', 'Address').split(":")
        self.data['livestatus'] = {'protocol': livestatus_split[0], 'address': livestatus_split[1]}
        if len(livestatus_split) == 3:
            self.data['livestatus']['port'] = int(livestatus_split[2])

        # Histou
        # histou_split = self.__settings.get('Histou', 'Address').split(":", 1)
        self.data['histou'] = {'prot': "http", 'address': self.__settings.get('Histou', 'Address')}

        # Influxdb
        self.data['influxdb'] = {'read': {'address': self.__settings.get('InfluxDB', 'Address_Read'),
                                          'db': self.__settings.get('InfluxDB', 'DB_Read'),
                                          'args': self.__settings.get('InfluxDB', 'DB_Read_Args')},
                                 'write': {'address': self.__settings.get('InfluxDB', 'Address_Write'),
                                           'db': self.__settings.get('InfluxDB', 'DB_Write'),
                                           'args': self.__settings.get('InfluxDB', 'DB_Write_Args')}}


def log_peformance():
    return Config.data['main']['log_performance']
