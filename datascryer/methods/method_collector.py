import inspect
import logging
import os
import sys

from datascryer.default_methods.simple_linear_regression import SimpleLinearRegression
from datascryer.methods.abc_forecast import ForecastMethod


class MethodCollector:
    classes = dict()

    def __init__(self, folders):
        build_in = [SimpleLinearRegression]
        try:
            from datascryer.default_methods.holt_winters import HoltWinters
            build_in.append(HoltWinters)
        except Exception as e:
            logging.getLogger(__name__).critical(str(e))

        for m in build_in:
            MethodCollector.classes[str.lower(m.__name__)] = m()

        for folder in folders:
            try:
                for file in os.listdir(folder):
                    try:
                        import_path = folder + "." + os.path.splitext(file)[0]
                        if str.endswith(import_path, "__"):
                            continue
                        import_path = import_path.replace("/", ".").replace("\\", ".")
                        __import__(import_path)
                        for c in inspect.getmembers(sys.modules[import_path], inspect.isclass):
                            if c[1] in ForecastMethod.__subclasses__():
                                MethodCollector.classes[str.lower(c[0])] = c[1]()
                            else:
                                if c[0] != "ForecastMethod":
                                    print(c[0] + " does not implement ForecastMethod")
                    except Exception as e:
                        logging.getLogger(__name__).critical("Loading method failed: " + str(e))
            except Exception as f:
                logging.getLogger(__name__).critical(f)
