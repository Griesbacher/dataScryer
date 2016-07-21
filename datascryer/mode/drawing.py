import logging
import sys
import time

from datascryer import livestatus
from datascryer.config import Config, log_peformance
from datascryer.helper.python import delta_ms, python_3
from datascryer.histou.histou import Histou
from datascryer.jobs.job_manager import JobManager

if python_3():
    from urllib.error import URLError
else:
    from urllib2 import URLError


def forecast_mode(time_for_calculations=10):
    if Config.data['livestatus']['protocol'] == "tcp":
        l = livestatus.Connector(
            ip=(Config.data['livestatus']['address'], Config.data['livestatus']['port']))
    elif Config.data['livestatus']['protocol'] == "unix":
        l = livestatus.Connector(soc=(Config.data['livestatus']['address']))
    else:
        sys.exit(
            "Livestatus protocol is unkown: " + Config.data['livestatus']['protocol'] + ". Allowed are tcp/unix"
        )
    h = Histou(protocol=Config.data['histou']['prot'], address=Config.data['histou']['address'])
    m = JobManager()

    config_host_service = {}

    if Config.data['main']['daemon']:
        try:
            while True:
                start = time.time()
                config_host_service = mainloop(job_config=config_host_service, live=l, histou=h, manager=m)
                if log_peformance():
                    logging.getLogger(__name__).debug("Updating config took: %dms" % delta_ms(start))
                time.sleep(Config.data['main']['update_rate'])
        except Exception as e:
            logging.getLogger(__name__).fatal(str(e), exc_info=True)
    else:
        logging.getLogger(__name__).info(
            "Running just once, and wait %ds to finish calculations" % time_for_calculations
        )
        start = time.time()
        mainloop(job_config=config_host_service, live=l, histou=h, manager=m)
        if log_peformance():
            logging.getLogger(__name__).debug("One cycle took: %dms" % delta_ms(start))
        time.sleep(time_for_calculations)
    m.stop()


def mainloop(job_config, live, histou, manager):
    l_start = time.time()
    host_services = live.get_host_services()
    if log_peformance():
        logging.getLogger(__name__).debug("Livestatusquery took: %dms" % delta_ms(l_start))

    for host, hv in host_services.items():
        config_names = []
        for service, sv in hv.items():
            config_names.append(
                {"host": host, "service": service, "command": sv['command'], "perf_labels": sv['perf_labels']}
            )
        host_service_config = None
        try:
            l_start = time.time()
            host_service_config = histou.get_config(hosts_services=config_names)
        except URLError as error:
            logging.getLogger(__name__).error("Could not connect to histou, to receive the config: " + str(error),
                                              exc_info=True)
        if host_service_config:
            if log_peformance():
                logging.getLogger(__name__).debug("Histouquery took: %dms" % delta_ms(l_start))

            i = 0
            for service, sv in hv.items():
                if host_service_config[i]:
                    if host not in job_config:
                        job_config[host] = {}
                    sv['config'] = host_service_config[i]
                    job_config[host][service] = sv
                i += 1
    manager.update_config(job_config)
    return job_config
