# PUGLI-S web

This internal website presents selected local products from the IAR PuMA
monitoring pipeline. It is a consumer of pipeline outputs, not the authority
for raw-data transfer or retention.

Usage:

* python update_puglieseweb.py to update the webpage according to the pulsar folder observations in the database folder.

Contents:
* last_obs.html contains the last observations and plots.
* by_psr.html   contains the full list of pulsars and observations by date with their corresponding plots.

Directories:
* database/     observations of each pulsar
* last_obs/     last observations of each pulsar

* images/ assets/  just web content

The pipeline keeps products such as observation JSON metadata, PFDs, PNG
plots, `.tim` files, residuals, and masks locally. Raw multi-GB `.fil` files
are staged separately after successful processing and transferred to the
storage cluster through Globus; they should not be placed in the website tree.
Operational `.par` files may also be managed outside Git on the IAR cluster.

Website update failures must not be interpreted as successful end-to-end
observation processing. A future scheduled pipeline should quarantine failed
observations with a reason while continuing with other ready inputs.
