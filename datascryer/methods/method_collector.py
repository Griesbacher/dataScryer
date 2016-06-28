import inspect
import os
import sys

from datascryer.methods.abc_forecast import ForecastMethod


class MethodCollector:
    classes = dict()

    def __init__(self, folders):
        for folder in folders:
            for file in os.listdir(folder):
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
