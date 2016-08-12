# Validate with database
# if necessary, could be used time to compare.
# if url time is older than bd time, reject

# from tacker.db.vm import vm_db
import logging
from six.moves.urllib import parse as urlparse
from tacker import wsgi
import webob.dec
# from tacker.vm.monitor_drivers.token import Token
LOG = logging.getLogger(__name__)


class AlarmReceiver(wsgi.Middleware):
    """Make a request context from keystone headers."""

    @webob.dec.wsgify
    def __call__(self, req):
        # if req.method != 'POST':
        #    return
        url = req.url
        LOG.debug(_('hll: %s'), url)
        device_id, params = self.handle_url(req.url)
        LOG.debug(_('dvc: %s'), device_id)
        self.validate_url(url)
        return self.application

    def handle_url(self, url):
        parts = urlparse.urlparse(url)
        p = parts.path.split('/')
        LOG.debug(_('Alarm url triggered: %s'), url)
        if len(p) != 6:
            return None
        if any((p[0] != '', p[2] != 'vnfs')):
            return None
        qs = urlparse.parse_qs(parts.query)
        params = dict((k, v[0]) for k, v in qs.items())
        return p[3], params

    def validate_url(self, url):
        return True
