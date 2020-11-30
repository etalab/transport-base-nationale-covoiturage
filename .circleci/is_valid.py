import sys
import json
import logging

valid = json.load(sys.stdin)['report']['valid']
if valid:
    logging.info("file is valid according to the national schema")
    sys.exit(0)
else:
    logging.info("file is NOT valid according to the national schema")
    sys.exit(1)
