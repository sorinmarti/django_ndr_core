from html import escape

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import FormView

from ndr_core.admin_forms.admin_forms import ConnectWithNdrCoreForm
from ndr_core.views import create_robots_txt_view, create_sitemap_view


class ConnectWithNdrCoreOrgView(LoginRequiredMixin, FormView):
    """View to preview the robots.txt file."""

    template_name = 'ndr_core/admin_views/overview/configure_seo.html'
    form_class = ConnectWithNdrCoreForm
    success_url = reverse_lazy('ndr_core:seo_ndrcore_org')

    def form_valid(self, form):
        """Render the robots.txt file."""
        return super().form_valid(form)


class RobotsFileView(LoginRequiredMixin, View):
    """View to preview the robots.txt file."""

    template_name = 'ndr_core/admin_views/overview/configure_seo.html'

    def get(self, request, *args, **kwargs):
        """Render the robots.txt file."""
        robots_file = create_robots_txt_view(request, as_string=True)
        robots_file = robots_file.replace('\n', '<br>')
        return render(request, self.template_name, {'robots_txt': robots_file})


class SitemapFileView(LoginRequiredMixin, View):
    """View to preview the sitemap.xml file."""

    template_name = 'ndr_core/admin_views/overview/configure_seo.html'

    def get(self, request, *args, **kwargs):
        """Render the robots.txt file."""
        sitemap_file = create_sitemap_view(request, as_string=True)
        sitemap_file = escape(sitemap_file)
        sitemap_file = sitemap_file.replace('\n', '<br>')
        return render(request, self.template_name, {'sitemap_xml': sitemap_file})
