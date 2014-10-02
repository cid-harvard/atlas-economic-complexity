from atlas import celery_tasks

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
        request.prerender = True

        return None

    def process_response(self, request, response):

        # Deal with django streaming responses
        if response.streaming:
            return response

        # If prerender is not needed, just return
        if not (hasattr(request, "prerender") and request.prerender):
            return response

        # TODO: pass in HTML somehow, since this doesn't work. Maybe write to
        # tempfile and pass file:// url?
        promise = celery_tasks.prerender.delay(response.content)
        response.content = promise.get()

        return response
