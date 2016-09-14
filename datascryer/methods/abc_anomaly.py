from abc import ABCMeta, abstractmethod


class AnomalyMethod:
    __metaclass__ = ABCMeta

    @abstractmethod
    def search_anomaly(self, options, lookback_range,  lookback_data):
        raise NotImplementedError()
