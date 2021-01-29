'''
############################################## ASIDE ##############################################
This module will contain all the constant variables and functions which will be used by all 
    other modules.
'''

# Constants #
class constants:
    # This enables the logging to the screen
    verbose = True

# Functions #
def pv(s: str): # pv ---> print verbose
    if constants.verbose:
        print(s)