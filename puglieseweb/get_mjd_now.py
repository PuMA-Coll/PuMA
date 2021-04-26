#!/usr/bin/python
from astropy.time import Time
print('DATE UTC: {}\nMJD: {:.5f}'.format(Time.now(),Time.now().mjd))


