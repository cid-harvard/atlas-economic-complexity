from atlas import celery_tasks
from observatory import helpers

import celery
from django.conf import settings

import logging
import os
import tempfile

logger = logging.getLogger(__name__)


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

        # TODO: AFAIK there is no better way to send this html to phantomjs
        temp = tempfile.NamedTemporaryFile(dir="/tmp/ramdisk",
                                           prefix="celery-temp-file-",
                                           suffix=".html")
        temp.write(response.content)
        temp.flush()
        os.chmod(temp.name, 0755)

        url = "http://127.0.0.1:8000/%s%s" % (os.path.basename(temp.name),
                                              request.GET.urlencode())

        # Try to prerender, if it times out just return the original
        try:
            prerender = celery_tasks.prerender.s(url)
            filename = helpers.url_to_hash(request.path, request.GET) + ".png"
            get_image = celery_tasks\
                .prerendered_html_to_image.s(name=filename,
                                             path=settings.STATIC_IMAGE_PATH)
            result = celery.chain(prerender, get_image)()
            response.content = result.parent.get(timeout=10)
            return response
        except Exception:
            if "result" in locals():
                result.forget()
            logger.exception("Error occurred while prerendering page.")
            raise
        finally:
            temp.close()
