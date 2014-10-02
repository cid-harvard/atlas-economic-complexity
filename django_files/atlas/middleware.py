
class PrerenderMiddleware(object):
    """Middleware to prerender crawler requests with phantomjs."""

    def process_request(self, request):

        # See if prerender is needed
        escaped_fragment = request.GET.get('_escaped_fragment_', None)
        if not escaped_fragment:
            return None

        # Pop off _escaped_fragment_
        request.GET = request.GET.copy()
        request.GET.pop('_escaped_fragment_')

        return None

    def process_response(self, request, response):

        # Deal with django streaming responses
        if response.streaming:
            return response

        #if "_escaped_fragment_" in request.args:
        response.content = response.content
        return response
