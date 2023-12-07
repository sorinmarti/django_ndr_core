"""Views for the messages section in the admin panel. """
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DeleteView, DetailView

from ndr_core.admin_views.admin_views import AdminViewMixin
from ndr_core.models import NdrCoreUserMessage


class ConfigureMessages(AdminViewMixin, LoginRequiredMixin, View):
    """View to add/edit/delete Messages. """

    def get(self, request, *args, **kwargs):
        """GET request for this view. """

        context = {'ndr_messages': NdrCoreUserMessage.objects.filter(message_archived=False).order_by('-message_time')}

        return render(self.request, template_name='ndr_core/admin_views/overview/configure_messages.html',
                      context=context)


class ArchivedMessages(AdminViewMixin, LoginRequiredMixin, View):
    """View to add/edit/delete Messages. """

    def get(self, request, *args, **kwargs):
        """GET request for this view. """

        context = {'ndr_messages': NdrCoreUserMessage.objects.filter(message_archived=True).order_by('-message_time')}

        return render(self.request, template_name='ndr_core/admin_views/overview/configure_messages.html',
                      context=context)


class MessagesView(AdminViewMixin, LoginRequiredMixin, DetailView):
    """ View to show a user message."""
    model = NdrCoreUserMessage
    template_name = 'ndr_core/admin_views/overview/configure_messages.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['ndr_messages'] = NdrCoreUserMessage.objects.filter(message_archived=False).order_by('-message_time')
        return context


class MessagesDeleteView(AdminViewMixin, LoginRequiredMixin, DeleteView):
    """ View to delete a message. Asks to confirm."""

    model = NdrCoreUserMessage
    success_url = reverse_lazy('ndr_core:configure_messages')
    template_name = 'ndr_core/admin_views/delete/message_confirm_delete.html'


@login_required
def archive_message(request,pk):
    """TODO """
    try:
        message = NdrCoreUserMessage.objects.get(pk=pk)
        message.message_archived = True
        message.save()
        messages.success(request, "Message archived")
    except NdrCoreUserMessage.DoesNotExist:
        messages.error(request, "Message not found")

    return redirect('ndr_core:configure_messages')


@login_required
def delete_all_messages(request):
    """TODO Doc and CONFIRM"""
    NdrCoreUserMessage.objects.all().delete()
    messages.success(request, "Deleted all messages")
    return redirect('ndr_core:configure_messages')
