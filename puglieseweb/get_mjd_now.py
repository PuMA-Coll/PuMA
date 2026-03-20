#!/usr/bin/env python3
from astropy.time import Time
print(('DATE UTC: {}\nMJD: {:.5f}'.format(Time.now(),Time.now().mjd)))


