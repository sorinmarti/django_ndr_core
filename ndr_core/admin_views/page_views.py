""" This file contains the views for the page management. It lets you create, edit and delete pages."""
import os
import shutil

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.staticfiles import finders
from django.db.models import Max
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DeleteView, CreateView, DetailView, UpdateView

from ndr_core.admin_forms.page_forms import PageCreateForm, PageEditForm, FooterForm
from ndr_core.models import NdrCorePage
from ndr_core.ndr_settings import NdrSettings


class ManagePages(LoginRequiredMixin, View):
    """The ManagePages view shows a table of all pages in an installation and lets you define their order. You can
      edit, delete and create pages here. """

    def get(self, request, *args, **kwargs):
        """GET request for this view. """

        context = {'pages': NdrCorePage.objects.filter(parent_page=None).order_by('index')}

        return render(self.request,
                      template_name='ndr_core/admin_views/configure_pages.html',
                      context=context)


class ManagePageFooter(LoginRequiredMixin, View):
    """TODO """

    def get(self, request, *args, **kwargs):
        """GET request for this view. """

        context = {'pages': NdrCorePage.objects.filter(parent_page=None).order_by('index'),
                   'footer_form': FooterForm()}

        return render(self.request,
                      template_name='ndr_core/admin_views/configure_pages.html',
                      context=context)

    def post(self, request, *args, **kwargs):
        """POST request for this view. Gets executed when setting values are saved."""

        form = FooterForm(request.POST)
        form.save_list()
        context = {'pages': NdrCorePage.objects.filter(parent_page=None).order_by('index'),
                   'footer_form': form}

        messages.success(request, "Saved Changes")

        return render(self.request,
                      template_name='ndr_core/admin_views/configure_pages.html',
                      context=context)


class PageDetailView(LoginRequiredMixin, DetailView):
    """The PageDetailView shows the details of a page. It is shown when selecting a page in the table.
    The list of pages is still shown on the right side."""

    model = NdrCorePage
    template_name = 'ndr_core/admin_views/configure_pages.html'

    def get_context_data(self, **kwargs):
        context = super(PageDetailView, self).get_context_data(**kwargs)
        context['pages'] = NdrCorePage.objects.filter(parent_page=None).order_by('index')
        return context


class PageCreateView(LoginRequiredMixin, CreateView):
    """ View to create a new NdrCorePage """

    model = NdrCorePage
    form_class = PageCreateForm
    success_url = reverse_lazy('ndr_core:configure_pages')
    template_name = 'ndr_core/admin_views/page_create.html'

    def form_valid(self, form):
        """Overwrites form_valid function of CreateView. Sets the index of the newly created page object and creates
         a template to save in the ndr apps template folder."""

        response = super(PageCreateView, self).form_valid(form)

        max_index = NdrCorePage.objects.aggregate(Max('index'))
        new_index = max_index["index__max"] + 1
        self.object.index = new_index
        self.object.save()

        new_filename = f'{NdrSettings.APP_NAME}/templates/{NdrSettings.APP_NAME}/{form.cleaned_data["view_name"]}.html'
        if os.path.isfile(new_filename):
            messages.error(self.request, "The file name already existed. No new template was generated.")
        else:
            if self.object.page_type == self.object.PageType.TEMPLATE:
                base_file = finders.find('ndr_core/app_init/template.html')
                shutil.copyfile(base_file, new_filename)
            elif self.object.page_type == self.object.PageType.SIMPLE_SEARCH:
                base_file = finders.find('ndr_core/app_init/search.html')
                shutil.copyfile(base_file, new_filename)
            elif self.object.page_type == self.object.PageType.SEARCH:
                base_file = finders.find('ndr_core/app_init/search.html')
                shutil.copyfile(base_file, new_filename)
            elif self.object.page_type == self.object.PageType.COMBINED_SEARCH:
                base_file = finders.find('ndr_core/app_init/combined_search.html')
                shutil.copyfile(base_file, new_filename)
            elif self.object.page_type == self.object.PageType.FILTER_LIST:
                base_file = finders.find('ndr_core/app_init/filtered_list.html')
                shutil.copyfile(base_file, new_filename)
            elif self.object.page_type == self.object.PageType.CONTACT:
                base_file = finders.find('ndr_core/app_init/contact.html')
                shutil.copyfile(base_file, new_filename)
            elif self.object.page_type == self.object.PageType.FLIP_BOOK:
                base_file = finders.find('ndr_core/app_init/flip_book.html')
                shutil.copyfile(base_file, new_filename)
            elif self.object.page_type == self.object.PageType.ABOUT_PAGE:
                base_file = finders.find('ndr_core/app_init/about_us.html')
                shutil.copyfile(base_file, new_filename)
        return response


class PageEditView(LoginRequiredMixin, UpdateView):
    """ View to edit an existing NdrCorePage """

    model = NdrCorePage
    form_class = PageEditForm
    success_url = reverse_lazy('ndr_core:configure_pages')
    template_name = 'ndr_core/admin_views/page_edit.html'

    def form_valid(self, form):
        """Overwrites form_valid function of CreateView. Sets the index of the newly created page object and creates
        a template to save in the ndr apps template folder."""
        updated_instance = form.save(commit=False)
        original_instance = NdrCorePage.objects.get(pk=updated_instance.pk)

        old_filename = f'{NdrSettings.APP_NAME}/templates/{NdrSettings.APP_NAME}/{original_instance.view_name}.html'
        new_filename = f'{NdrSettings.APP_NAME}/templates/{NdrSettings.APP_NAME}/{updated_instance.view_name}.html'

        if old_filename != new_filename:
            os.rename(old_filename, new_filename)

        response = super(PageEditView, self).form_valid(form)
        return response


class PageDeleteView(LoginRequiredMixin, DeleteView):
    """ View to delete an NdrCorePage from the database. Asks to confirm.
    This function also deletes the created HTML template. """

    model = NdrCorePage
    success_url = reverse_lazy('ndr_core:configure_pages')
    template_name = 'ndr_core/admin_views/page_confirm_delete.html'

    def form_valid(self, form):
        """Overwrites form_valid function of DeleteView. Deletes the object and its template."""

        filename = f'{NdrSettings.APP_NAME}/templates/{NdrSettings.APP_NAME}/{self.object.view_name}.html'
        if os.path.isfile(filename):
            os.remove(filename)
        else:
            messages.warning(self.request, "HTML template to delete was not found.")

        return super(PageDeleteView, self).form_valid(form)


@login_required
def move_page_up(request, pk):
    """ NdrCorePages have an index to determine in which order they are displayed.
    This function moves up a page in the order.

    :param request: The page's request object
    :param pk: The primary key of the NdrCorePage to move up
    :return: A redirect response to 'configure_pages'
    """

    try:
        this_page = NdrCorePage.objects.get(id=pk)
        # Get the list in which we want to move: the same as the page is in
        values = list(NdrCorePage.objects.filter(parent_page=this_page.parent_page).order_by('index').values_list('index', flat=True))
        this_pages_index = values.index(this_page.index)
        if this_pages_index == 0:
            messages.warning(request, "Page is already on top")
        else:
            other_page = NdrCorePage.objects.get(index=values[this_pages_index-1])
            switch_value = other_page.index
            other_page.index = this_page.index
            this_page.index = switch_value
            this_page.save()
            other_page.save()
    except NdrCorePage.DoesNotExist:
        messages.error(request, "Page does not exist")
    return redirect('ndr_core:configure_pages')
