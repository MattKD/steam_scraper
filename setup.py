from setuptools import setup, find_packages

setup(
    name='steam_scraper',
    version='1.0.0',
    url='https://github.com/MattKD/steam_scraper.git',
    author='Matt Donovan',
    description='Tiny library to scrape app data from Steam store',
    packages=['steam_scraper'],    
    install_requires=['certifi >= 2019.3.9', 'pycurl >= 7.43.1', 
                      'lxml >= 4.3.2'],
)
