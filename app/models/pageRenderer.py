import logging

from django.http import Http404, HttpResponse
from django.template import Template, RequestContext
from django.utils import timezone

from webdb.pages import Pages

logger = logging.getLogger('naviswiss')

class PageRenderer:
    @staticmethod
    def render(request, page_id, context=None, status=200):
        print (page_id)
        if context is None:
            context = {}
        print(context)
        page = Pages.get_page(page_id)
        if page is None or page.status != 'Active':
            raise Http404("Unable to find page")

        html = page.get_text()

        try:
            template = Template(html)
        except Exception as e:
            logger.error("Unable to load template: {}".format(e.args))
            print("Unable to load template: {}".format(e.args))
            template = None

        # Add page title to context if it isn't already set
        if 'title' not in context:
            context['title'] = page.title

        # inject referrer into context if the controller hasn't already
        if not context.get('referrer'):
            context['referrer'] = request.META.get('HTTP_REFERRER')

        if not context.get('today'):
            context['today'] = timezone.now().strftime('%Y-%m-%d')

        try:
            ctx = RequestContext(request, context)
        except Exception as e:
            logger.error("Unable to load Context: {}".format(e.args))
            ctx = None

        if template and ctx:
            return HttpResponse(template.render(ctx), status=status)
        else:
            logger.debug("Could not find page")
            raise Http404("Not found")
