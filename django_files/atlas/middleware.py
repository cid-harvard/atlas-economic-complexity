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
        if request.resolver_match and ("observatory.views.explore"
                                       != request.resolver_match.url_name):
            return response

        # Deal with django streaming responses, these don't need to be
        # prerendered anyway.
        if response.streaming:
            return response

        # TODO: AFAIK there is no better way to send this html to phantomjs
        temp = tempfile.NamedTemporaryFile(dir="/tmp/ramdisk",
                                           prefix="celery-temp-file-",
                                           suffix=".html",
                                           delete=False)
        temp.write(response.content)
        temp.flush()
        os.chmod(temp.name, 0755)

        url = settings.STATIC_IMAGE_PHANTOMJS_URL + \
            "%s" % os.path.basename(temp.name)

        # Try to prerender, if it times out just return the original
        try:

            prerender = celery_tasks.prerender.s(url)
            filename = helpers.url_to_hash(request.path, request.GET) + ".png"
            get_image = celery_tasks\
                .prerendered_html_to_image.s(name=filename,
                                             path=settings.STATIC_IMAGE_PATH)

            if hasattr(request, "bot_crawl") and request.bot_crawl:
                # If prerender is needed, wait for phantomjs
                result = celery.chain(prerender, get_image)()
                response.content = result.parent.get(timeout=15)
                return response
            else:
                # Otherwise, generate static image in the background, if it
                # isn't already there
                if not os.path.exists(os.path.join(settings.STATIC_IMAGE_PATH,
                                                   filename)):
                    result = celery.chain(prerender, get_image)()
                return response

        except Exception:
            if "result" in locals():
                result.forget()
            logger.exception("Error occurred while prerendering page.")
            raise
        finally:
            temp.close()
