from metrics import MetricsProvider

class MetricsMiddleware(object):

    def process_view(self, request, view_func, view_args, view_kwargs):
        full_view_name = '{}.{}'.format(view_func.__module__, view_func.__name__)
        m = MetricsProvider.get_metrics(view_func.__name__)
        request.middleware_metrics = m

    def process_response(self, request, response):
        if hasattr(request, 'middleware_metrics'):
            del request.middleware_metrics

        return response
