import os

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths


extra_files = package_files('datascryer')

setup(
    version="0.0.2",

    name="DataScryer",
    description="DataScryer - Framework to predict future performancedata.",
    author="Philip Griesbacher",
    author_email="philip.griesbacher@consol.de",
    url="https://github.com/Griesbacher/dataScryer",

    packages=["datascryer"],
    package_data={'': extra_files},
    scripts=['bin/dataScryer.py'],

    license="GPLv3",
    install_requires=[
        "jsonschema", 'requests'
    ],
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
    zip_safe=True
)
