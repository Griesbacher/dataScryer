from datascryer.default_methods.holt_winters import HoltWinters
from datascryer.default_methods.stddev_anomaly import StddevAnomaly
from datascryer.methods.abc_anomaly import AnomalyMethod


class HoltWintersAnomaly(AnomalyMethod):
    def search_anomaly(self, options, lookback_range, lookback_data):
        raw_data = []
        for d in lookback_data:
            raw_data.append(d[1])

        start = lookback_data[0][0]
        end = lookback_data[len(lookback_data) - 1][0]

        resolution = 100
        if 'resolution' in options:
            resolution = options['resolution']
        raw_data = HoltWinters().trim_data(raw_data, resolution)

        forecast, _, _ = HoltWinters().find_best_function(list(raw_data[:int(len(raw_data) / 3 * 2)]), 100)

        sigma = 3
        if 'sigma' in options:
            sigma = options['sigma']
        e = StddevAnomaly().detect_anomaly(raw_data, forecast, sigma)

        anomaly_per_ten = 1
        if 'errors_per_ten' in options:
            anomaly_per_ten = options['anomaly_per_ten']
        r = StddevAnomaly().filter_errors(e, hits=anomaly_per_ten)

        step = (end - start) / resolution
        x_forecast = [start + y * step for y in range(len(r))]
        result = []
        for e in list(zip(x_forecast, r)):
            if e[1] is not None:
                result.append(e)
        return result
