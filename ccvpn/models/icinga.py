import json
import re
import requests
import socket
from beaker import cache


class IcingaError(Exception):
    pass


class IcingaQuery(object):
    def __init__(self, urlbase, auth):
        self.baseurl = urlbase
        self.auth = auth

        try:
            content = self._get_availcgi()
            data = json.loads(content)
            self.report = data['avail']['service_availability']['services']
        except (requests.RequestException, socket.timeout) as e:
            raise IcingaError('failed to connect: ' + str(e))
        except (ValueError, KeyError) as e:
            raise IcingaError('failed to decode icinga response (%s)' % str(e))

    @cache.cache_region('short_term')
    def _get_availcgi(self):
        hostservices = 'all^all'
        timeperiod = 'last31days'
        backtrack = 4
        url = '/avail.cgi?hostservice=%s&timeperiod=%s&backtrack=%d&jsonoutput'
        url = url % (hostservices, timeperiod, backtrack)
        r = requests.get(self.baseurl + url,
                         auth=self.auth, verify=False, timeout=2)
        content = r.content.decode('utf-8')

        # When querying services availability, icinga can break the JSON
        content = re.sub(',\n*(\]|\})', '\\1', content)

        return content

    def get_uptime(self, host, service):
        try:
            def fn(h):
                return h['host_name'] == host and \
                       h['service_description'] == service
            svcdata = next(filter(fn, self.report))
            uptime = int(svcdata['percent_known_time_ok'])
        except (KeyError, ValueError) as e:
            raise IcingaError('failed to parse icinga report (%s)' % str(e),
                              host, service)
        except StopIteration:
            raise IcingaError('host/service unknown to icinga', host, service)
        return uptime

