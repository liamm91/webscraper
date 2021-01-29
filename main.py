"""
To do:

make function to get the html request
make web crawler class
make multi threading
make logging
"""

__author__ = "Liam Major"
__version__ = "0.1"

# verbose = True:
# def pv(text: str): # pv = print verbose
#     if verbose:
#         print(text)

from src import db, logger, crawler
from src.consts import *

print(crawler.scrape_attrs('<a href="https://stackoverflow.blog" class="fr">company blog</a>'))
print(crawler.scrape_attrs('<a href="https://stackoverflow.com/help" class="js-gps-track" data-gps-track="site_switcher.click({ item_type:14 })">help</a>'))
