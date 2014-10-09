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
        bot_crawl = request.GET.get('_escaped_fragment_', None)
        if not bot_crawl:
            return None

        # Pop off _escaped_fragment_
        request.GET = request.GET.copy()
        request.GET.pop('_escaped_fragment_')
        request.bot_crawl = True

        return None

    def process_response(self, request, response):

        # If this is not an explore page, no need to prerender
        if "observatory.views.explore" != request.resolver_match.url_name:
            return response

        # Deal with django streaming responses, these don't need to be
        # prerendered anyway.
        if response.streaming:
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
            if not (hasattr(request, "bot_crawl") and request.bot_crawl):
                # If prerender is not needed, just return after firing the
                # celery task.
                return response
            else:
                # Otherwise wait for the response
                response.content = result.parent.get(timeout=15)
                return response

        except Exception:
            if "result" in locals():
                result.forget()
            logger.exception("Error occurred while prerendering page.")
            raise
        finally:
            temp.close()
