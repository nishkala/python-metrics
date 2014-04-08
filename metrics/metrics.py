import logging
import json
import threading
import uuid
from datetime import datetime
from collections import OrderedDict

from contextdecorator import ContextDecorator
from exceptions import MetricsObjectClosedError

logger = logging.getLogger('metrics')
threadLocal = threading.local()


class MetricsProvider(ContextDecorator):

    def __init__(self, name):
        self.name = name

    def __enter__(self):
        self.m = MetricsProvider.get_metrics(self.name)
        return self.m

    def __exit__(self, type, value, traceback):
        if self.m:
            self.m.close()
            del self.m
        return False

    @classmethod
    def get_metrics(cls, name):
        guid = getattr(threadLocal, 'metrics_guid', None)
        if not guid:
            guid = str(uuid.uuid4())
            threadLocal.metrics_guid = guid
        return Metrics(name, guid)


class Metrics(object):
    guid = None
    name = None
    parent = None
    identity_user_id = None
    start_time = None
    end_time = None
    counts = None
    exceptions = None

    is_open = True

    def __init__(self, name, unique_id, parent=None):
        self.name = name
        self.guid = unique_id
        #self.parent = parent.guid
        self.start_time = datetime.now()
        self.counts = {}
        self.exceptions = {}

    def __del__(self):
        if self.is_open:
            self.close()

    def close(self):
        if self.is_open:
            self.end_time = datetime.now()
            self.is_open = False
            logger.info(self._jsonify())

    def set_identity_user_id(self, identity_username):
        self.identity_user_id = identity_username

    def add_count(self, event_name, number):
        if self.is_open:
            self.counts[event_name] = self.counts.get(event_name, 0) + number
        else:
            raise MetricsObjectClosedError("Attempted to use closed metrics object")

    def add_exception(self, exception):
        if self.is_open:
            exception_name = exception.__class__.__name__
            self.exceptions[exception_name] = self.exceptions.get(exception_name, 0) + 1
        else:
            raise MetricsObjectClosedError("Attempted to use closed metrics object")

    def _jsonify(self):
        obj = OrderedDict([
            ('GUID', self.guid),
            ('name', self.name),
            ('identity_user_id', self.identity_user_id),
            ('start_time', self.start_time.isoformat()),
            ('end_time', self.end_time.isoformat()),
            ('total_time', (self.end_time - self.start_time).total_seconds()),
            ('counters', self.counts),
            ('exceptions', self.exceptions),
        ])
        return json.dumps(obj)
