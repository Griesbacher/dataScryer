from datascryer.methods.abc_forecast import ForecastMethod


class SimpleLinearRegression(ForecastMethod):
    def calc_slr(self, lookback_data):
        sum_x, sum_y = self.sum_x_y(lookback_data)
        sum_x_2, _ = self.sum_x_y(lookback_data, 2)
        sum_x_y = sum([(x * y) for (x, y) in lookback_data])
        n = float(len(lookback_data))
        b = (n * sum_x_y - sum_x * sum_y) / (n * sum_x_2 - pow(sum_x, 2))
        a = (1 / n * sum_y) - b * 1 / n * sum_x
        if b == 0:
            return lambda x: a, lambda y: self.INF
        else:
            return lambda x: b * x + a, lambda y: (y - a) / b

    def calc_forecast(self, forecast_start, forecast_range, forecast_interval, lookback_range, lookback_data):
        return self.gen_forecast_data(
            func=self.calc_slr(lookback_data=lookback_data)[0],
            forecast_start=forecast_start,
            forecast_range=forecast_range,
            forecast_interval=forecast_interval
        )

    def calc_intersection(self, forecast_start, forecast_range, forecast_interval, lookback_range, lookback_data, y):
        return self.gen_intersection(
            self.gen_forecast_data(
                func=self.calc_slr(lookback_data=lookback_data)[0],
                forecast_start=forecast_start,
                forecast_range=forecast_range,
                forecast_interval=forecast_interval
            ),
            forecast_start=forecast_start,
            y=y
        )


def example_wiki():
    """
    Example based on: https://en.wikipedia.org/wiki/Simple_linear_regression#Numerical_example
    """
    data_x = [1.47, 1.50, 1.52, 1.55, 1.57, 1.60, 1.63, 1.65, 1.68, 1.70, 1.73, 1.75, 1.78, 1.80, 1.83]
    data_y = [52.21, 53.12, 54.48, 55.84, 57.20, 58.57, 59.93, 61.29, 63.11, 64.47, 66.28, 68.10, 69.92, 72.19, 74.46]
    data = list(zip(data_x, data_y))
    s = SimpleLinearRegression()
    print(s.calc_forecast(1.70, 0.3, 0.05, len(data), data))
    print(s.calc_intersection(1.70, 0.4, 0.05, len(data), data, 80))


if __name__ == "__main__":
    example_wiki()
