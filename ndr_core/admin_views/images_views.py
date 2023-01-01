from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Max
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, UpdateView, DeleteView, FormView

from ndr_core.admin_forms.images_forms import ImageCreateForm, LogoUploadForm, ImageEditForm
from ndr_core.models import NdrCoreImage
from ndr_core.ndr_settings import NdrSettings

image_groups = [
    {'name': 'figures',
     'label': 'Figure Images',
     'help_text': 'Upload images to be displayed in your text with captions and source information..'},
    {'name': 'logos',
     'label': 'Footer Partner Images',
     'help_text': 'Upload logos of your partner organisations and link them in the footer.'},
    {'name': 'people',
     'label': 'People Images',
     'help_text': 'Upload team members to create an "About Us" page.'},
    {'name': 'backgrounds',
     'label': 'Background Images',
     'help_text': 'Upload Images to be used as backgrounds of banners.'},
    {'name': 'elements',
     'label': 'Slideshow Images',
     'help_text': 'Upload Images to create slideshows from'},
]


class ConfigureImages(LoginRequiredMixin, View):
    """View to add/edit/delete Images. """

    def get(self, request, *args, **kwargs):
        """GET request for this view. """

        context = {'logo_path': f'{NdrSettings.APP_NAME}/images/logo.png',
                   'groups': image_groups}
        return render(self.request, template_name='ndr_core/admin_views/configure_images.html',
                      context=context)


class ImagesGroupView(LoginRequiredMixin, View):
    """Shows a group of images. """

    template_name = 'ndr_core/admin_views/configure_images.html'

    def get_context_data(self):
        context = {'logo_path': f'{NdrSettings.APP_NAME}/images/logo.png',
                   'groups': image_groups}
        group = self.kwargs['group']

        if group in NdrCoreImage.ImageGroup.values:
            images = NdrCoreImage.objects.filter(image_group=group).order_by('index_in_group')
            context['images'] = images
            context['title'] = NdrCoreImage.ImageGroup.get_label_by_value(group, NdrCoreImage.ImageGroup.choices)

        return context

    def get(self, request, *args, **kwargs):
        return render(self.request,
                      template_name=self.template_name,
                      context=self.get_context_data())


class ImagesCreateView(LoginRequiredMixin, CreateView):
    """ View to create a image """

    model = NdrCoreImage
    form_class = ImageCreateForm
    # success_url = reverse_lazy('ndr_core:configure_images')
    template_name = 'ndr_core/admin_views/image_create.html'

    def form_valid(self, form):
        response = super(ImagesCreateView, self).form_valid(form)
        max_index = NdrCoreImage.objects.filter(image_group=self.object.image_group).aggregate(Max('index_in_group'))
        new_index = max_index["index_in_group__max"] + 1
        self.object.index_in_group = new_index
        self.object.save()

        return response


class ImagesEditView(LoginRequiredMixin, UpdateView):
    """ View to edit an existing image """

    model = NdrCoreImage
    form_class = ImageEditForm
    success_url = reverse_lazy('ndr_core:configure_images')
    template_name = 'ndr_core/admin_views/image_edit.html'

    def form_valid(self, form):
        response = super(ImagesEditView, self).form_valid(form)
        return response


class ImagesDeleteView(LoginRequiredMixin, DeleteView):
    """ View to delete an image from the database. Asks to confirm."""

    model = NdrCoreImage
    success_url = reverse_lazy('ndr_core:configure_images')
    template_name = 'ndr_core/admin_views/image_confirm_delete.html'

    def form_valid(self, form):
        return super(ImagesDeleteView, self).form_valid(form)


class LogoUploadView(LoginRequiredMixin, FormView):
    """ View to upload a new logo image. """

    template_name = 'ndr_core/admin_views/logo_upload.html'
    form_class = LogoUploadForm
    success_url = reverse_lazy('ndr_core:configure_images')

    def form_valid(self, form):
        file_path = f"{NdrSettings.get_images_path()}/logo.png"
        f = form.files['upload_file']

        with open(file_path, 'wb+') as destination:
            for chunk in f.chunks():
                destination.write(chunk)
        messages.success(self.request, 'Changed logo file (You may need to reload this page).')
        return super().form_valid(form)


@login_required
def move_image_up(request, pk):
    """ NdrCoreImages have an index to determine in which order they are displayed.
    This function moves up a page in the order.

    :param request: The page's request object
    :param pk: The primary key of the NdrCorePage to move up
    :return: A redirect response to to 'configure_images'
    """

    try:
        image = NdrCoreImage.objects.get(id=pk)
        if image.index_in_group > 0:
            other_image = NdrCoreImage.objects.get(index_in_group=image.index_in_group-1,
                                                   image_group=image.image_group)
            old_index = image.index_in_group
            image.index_in_group = image.index_in_group - 1
            image.save()
            other_image.index_in_group = old_index
            other_image.save()
        else:
            messages.warning(request, "Image is already on top")
    except NdrCoreImage.DoesNotExist:
        messages.error(request, "Image does not exist")

    return redirect('ndr_core:view_images', group=image.image_group)
