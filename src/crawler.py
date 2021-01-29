'''
############################################## ASIDE ##############################################
This is the module that contains the web crawler.
The main focus of the crawler is to access a URI, and for every anchor tag in the page,
    make a new crawler to access the anchor tag's URI.

This module will handle opening links and retriving the anchor tags from it.
'''

# imports

from .consts import pv

# consts from here

atag_pattern = r"^<a.+<\/a>$"

# defining functions

def scrape_attrs(a):
    """
    This function scrapes the attributes from an HTML element
    
    Parameters:
        a (str): The HTML element to be scraped in string form

    Returns:
        r (dict): A map of the attribute-pairs
    """

    r = {}
    r["tag"] = a[1:a.index(" ")]
    for kv in a[a.index(" "):][1:].split(">")[0][:-1].split("\" "):
        # trimming first 3 characters out ' <a ' and the last char '>'

        # finding the first occurance of =" and splitting based on that index
        # then unpacking the results from split and mapping it
        k, v = kv.split('="')
        r[k] = v

    return r
    