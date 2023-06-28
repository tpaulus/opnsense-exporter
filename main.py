import time
from typing import Final, List

import prometheus_client
import urllib3
from environs import Env
from requests import Session

prometheus_client.REGISTRY.unregister(prometheus_client.GC_COLLECTOR)
prometheus_client.REGISTRY.unregister(prometheus_client.PLATFORM_COLLECTOR)
prometheus_client.REGISTRY.unregister(prometheus_client.PROCESS_COLLECTOR)

# Gateway Metrics
labels: Final[List[str]] = ["gateway_name"]  # TODO Include address as a label?

rtt = prometheus_client.Gauge("rtt", "Round Trip Time", labels)
rttd = prometheus_client.Gauge("rttd", "Round Trip Time Deviation", labels)
loss = prometheus_client.Gauge("loss", "Packet Loss Percentage (0-100)", labels)
up = prometheus_client.Gauge("up", "Gateway Status (up|down)", labels)


def scrape_gateway_metrics(session: Session, base_url: str):
    resp = session.get(f"{base_url}/api/routes/gateway/status")
    resp.raise_for_status()

    for gateway in resp.json().get('items', []):
        if gateway['delay'] == "~":
            rtt.labels(gateway_name=gateway['name']).set(-1)
        else:
            rtt.labels(gateway_name=gateway['name']).set(float(gateway['delay'][:-3]))

        if gateway['stddev'] == "~":
            rttd.labels(gateway_name=gateway['name']).set(-1)
        else:
            rttd.labels(gateway_name=gateway['name']).set(float(gateway['stddev'][:-3]))

        if gateway['loss'] == "~":
            loss.labels(gateway_name=gateway['name']).set(-1)
        else:
            loss.labels(gateway_name=gateway['name']).set(float(gateway['loss'][:-2]))

        up.labels(gateway_name=gateway['name']).set(0 if gateway['status'] == 'down' else 1)


if __name__ == '__main__':
    env = Env()
    env.read_env()

    # Start up the server to expose the metrics.
    with env.prefixed("METRICS_"):
        prometheus_client.start_http_server(env.int("PORT"))
        print(f"Serving metrics on {env.int('PORT')}")

    s = Session()
    with env.prefixed("OPNSENSE_"):
        s.auth = (env.str("KEY"), env.str("SECRET"))
        s.verify = env.bool("SSL_VERIFY")

        if not s.verify:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    while True:
        with env.prefixed("OPNSENSE_"):
            scrape_gateway_metrics(s, env.str("URL"))

        time.sleep(env.int("DELAY"))
