""" Views for the SEO section of the admin site. """
import os
from html import escape

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import FormView

from ndr_core.admin_forms.admin_forms import ConnectWithNdrCoreForm, UploadGoogleVerificationFileForm
from ndr_core.admin_views.admin_views import AdminViewMixin
from ndr_core.views import create_robots_txt_view, create_sitemap_view


class ConnectWithNdrCoreOrgView(AdminViewMixin, LoginRequiredMixin, FormView):
    """View to preview the robots.txt file."""

    template_name = 'ndr_core/admin_views/overview/configure_seo.html'
    form_class = ConnectWithNdrCoreForm
    success_url = reverse_lazy('ndr_core:seo_ndrcore_org')

    def form_valid(self, form):
        """Render the robots.txt file."""
        return super().form_valid(form)


class RobotsFileView(AdminViewMixin, LoginRequiredMixin, View):
    """View to preview the robots.txt file."""

    template_name = 'ndr_core/admin_views/overview/configure_seo.html'

    def get(self, request, *args, **kwargs):
        """Render the robots.txt file."""
        robots_file = create_robots_txt_view(request, as_string=True)
        robots_file = robots_file.replace('\n', '<br>')
        return render(request, self.template_name, {'robots_txt': robots_file})


class SitemapFileView(AdminViewMixin, LoginRequiredMixin, View):
    """View to preview the sitemap.xml file."""

    template_name = 'ndr_core/admin_views/overview/configure_seo.html'

    def get(self, request, *args, **kwargs):
        """Render the robots.txt file."""
        sitemap_file = create_sitemap_view(request, as_string=True)
        sitemap_file = escape(sitemap_file)
        sitemap_file = sitemap_file.replace('\n', '<br>')
        return render(request, self.template_name, {'sitemap_xml': sitemap_file})


class GoogleSearchConsoleVerificationView(AdminViewMixin, LoginRequiredMixin, View):
    """View to preview the Google Search Console verification file."""

    template_name = 'ndr_core/admin_views/overview/configure_seo.html'

    def get(self, request, *args, **kwargs):
        """Render the Google Search Console verification file."""
        # Check if there is a verification file
        file_path = os.path.join(settings.MEDIA_ROOT, f"uploads/seo/")
        google_search_console_verification_file = None
        if os.path.exists(file_path):
            for file in os.listdir(file_path):
                if file.startswith('google') and file.endswith('.html'):
                    google_search_console_verification_file = file
                    break

        context = {}
        if google_search_console_verification_file:
            context['google_search_console_verification_file'] = f"/media/uploads/seo/{google_search_console_verification_file}"
            context['form'] = None
        else:
            context['form'] = UploadGoogleVerificationFileForm()

        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        """Upload the Google Search Console verification file."""
        form = UploadGoogleVerificationFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data['file']
            file_path = os.path.join(settings.MEDIA_ROOT, f"uploads/seo/")
            os.makedirs(file_path, exist_ok=True)
            with open(os.path.join(file_path, file.name), 'wb') as destination:
                for chunk in file.chunks():
                    destination.write(chunk)
        return self.get(request, *args, **kwargs)


class GoogleSearchConsoleVerificationDeleteView(AdminViewMixin, LoginRequiredMixin, View):
    """View to delete the Google Search Console verification file."""

    template_name = 'ndr_core/admin_views/overview/configure_seo.html'

    def get(self, request, *args, **kwargs):
        """Delete the Google Search Console verification file."""
        file_path = os.path.join(settings.MEDIA_ROOT, f"uploads/seo/")
        if os.path.exists(file_path):
            for file in os.listdir(file_path):
                if file.startswith('google') and file.endswith('.html'):
                    os.remove(os.path.join(file_path, file))

        messages.success(request, 'The Google Search Console verification file has been deleted.')
        return redirect('ndr_core:seo_google')
