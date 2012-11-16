__author__ = 'Archy'

import logging
from datetime import datetime
from datetime import timedelta
import os.path
import os

logger = logging.getLogger("AutoSampler")
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
today_date = datetime.today()
datestring = today_date.strftime("%Y-%m-%d-%H-%M")
debugfilename = "c:/Users/Archy/Dropbox/Rehydroxylation/Logger/Autosampler/logs/rhx-" + datestring +\
                "_debug.log"
fh = logging.FileHandler(debugfilename)
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)
