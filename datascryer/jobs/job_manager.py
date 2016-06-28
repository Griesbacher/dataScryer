import logging

from datascryer.jobs.job import Job


class JobManager:
    def __init__(self):
        self.__jobs = {}

    def update_config(self, config):
        jobs_to_start = []
        job_to_stop = []
        for host, hv in config.items():
            for service, sv in hv.items():
                desc = (host, service, dict(sv))
                # print(desc)
                if host not in self.__jobs:
                    # job is new because host does not exits
                    jobs_to_start.append(desc)
                    self.__jobs[host] = {service: dict(sv)}
                elif host in self.__jobs and service not in self.__jobs[host]:
                    # job is new because service does not exits
                    jobs_to_start.append(desc)
                    self.__jobs[host][service] = dict(sv)
                elif host in self.__jobs and service in self.__jobs[host] \
                        and self.__jobs[host][service] != sv:
                    # job is known but config has changed
                    job_to_stop.append((host, service, self.__jobs[host][service]))
                    jobs_to_start.append(desc)
                    self.__jobs[host][service] = dict(sv)
        for host, hv in self.__jobs.items():
            for service, sv in hv.items():
                desc = (host, service, sv)
                if host not in config:
                    # job is outdated because no config for host exists
                    job_to_stop.append(desc)
                elif host in config and service not in config[host]:
                    # job is outdated because no config for service exists
                    job_to_stop.append(desc)

        self.__start_jobs(jobs_to_start)
        self.__stop_jobs(job_to_stop)

    @staticmethod
    def __stop_jobs(jobs):
        if not jobs:
            return
        for j in jobs:
            logging.getLogger(__name__).debug("Stopping job: %s %s" % (j[0], j[1]))
            j[2]['job'].stop()

    def __start_jobs(self, jobs):
        if not jobs:
            return
        for j in jobs:
            logging.getLogger(__name__).debug("Starting job: %s %s" % (j[0], j[1]))
            self.__jobs[j[0]][j[1]]['job'] = Job(j)
            self.__jobs[j[0]][j[1]]['job'].start()

    def stop(self):
        for host, hv in self.__jobs.items():
            for service, sv in hv.items():
                sv['job'].stop()
