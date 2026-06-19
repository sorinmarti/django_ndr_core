"""Signal handlers for ndr_core."""
from django.db.models.signals import post_delete
from django.dispatch import receiver


@receiver(post_delete, sender='ndr_core.NdrCoreUiElementItem')
def delete_js_module_package_on_item_delete(sender, instance, **kwargs):
    """Delete the uploaded zip file when a JS module item is removed."""
    if instance.js_module_package:
        instance.js_module_package.delete(save=False)