from django.test import TestCase

# Create your tests here.
import  logging

log = logging.getLogger('interface')
log.debug("1111")
log.info("info")
log.error("error11")
log.warn("warn...")