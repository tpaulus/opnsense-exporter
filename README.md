# opnsense-exporter

Currently, this just exports Gateway Metrics

### Relevant Environment Variables

* `OPNSENSE_URL` - OPNsense URL, e.g. `https://10.0.10.1`
* `OPNSENSE_KEY` - API Key
* `OPNSENSE_SECRET` - API Secret
* `OPNSENSE_SSL_VERIFY` - `true|false` Enable/Disable SSL Verification
* `METRICS_PORT` - Port on which to serve metrics
* `DELAY` - Sleep time in seconds between scraping OPNSense