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

    @webob.dec.wsgify
    def __call__(self, req):
        LOG.debug(_('hll: %s'), req.url)
        return self.application

    def process_request(self, req):
        if req.method != 'POST':
            return
        url = req.url
        LOG.debug(_('tung triggered: %s'), url)
        device_id, params = self.handle_url(req.url)
        self.validate_url(url)
#        token = Token(username='admin', password='devstack',
#                      auth_url="http://127.0.0.1:35357/v2.0", tenant_name="admin")
#        token_identity = token.create_token()

        # LOG.debug('Alarm url %s', token['id'])

#        req.headers['X-Auth-Token'] = token_identity
        return None

    def handle_url(self, url):
        # alarm_url = 'http://host:port/v1.0/vnfs/vnf-uuid/monitoring-policy-name/action-name?key=8785'
        parts = urlparse.urlparse(url)
        p = parts.path.split('/')
        LOG.debug(_('Alarm url triggered: %s'), url)
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

#    @classmethod
#    def factory(cls, global_config, **local_config):
#        """Paste factory."""
#        def _factory(app):
#            return cls(app, global_config, **local_config)
#        return _factory


#def webhook_filter_factory(global_conf, **local_conf):
#    def _factory(app):
#        return AlarmReceiver(app)
#    return _factory
