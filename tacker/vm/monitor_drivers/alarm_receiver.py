# Validate with database
# if necessary, could be used time to compare.
# if url time is older than bd time, reject

# from tacker.db.vm import vm_db
from tacker import wsgi
import logging
from six.moves.urllib import parse as urlparse

LOG = logging.getLogger(__name__)


class AlarmReceiver(wsgi.Middleware):

    def process_request(self, request):
        if request.method != 'POST':
            return
        url = request.url
        LOG.debug('Alarm url %s', url)
        device_id, params = self.handle_url(request.url)
        self.validate_url(url)

    def handle_url(self, url):
        # alarm_url = 'http://host:port/v1.0/vnfs/vnf-uuid/monitoring-policy-name/action-name?key=8785'
        parts = urlparse.urlparse(url)
        p = parts.path.split('/')

        # expected: ['', 'v1.0', 'vnfs', 'vnf-uuid', 'monitoring-policy-name', 'action-name']
        if len(p) != 6:
            return None

        if any((p[0] != '', p[2] != 'vnfs')):
            return None
        qs = urlparse.parse_qs(parts.query)
        params = dict((k, v[0]) for k, v in qs.items())
        return p[3], params

    def validate_url(self, url):
        '''Validate with db'''
        return True
