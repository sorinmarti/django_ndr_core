""" This file holds the ndr_import_manifests management command class.
TODO ATTENTION: This is for testing purposes only and does not yet work for production."""
import json
import os

from django.core.management.base import BaseCommand
from ndr_core.models import NdrCoreManifest


class Command(BaseCommand):
    help = 'This command imports manifests.'

    def add_arguments(self, parser):
        parser.add_argument("directory", type=str, help="Directory where the manifests lie.")

    def handle(self, *args, **options):
        # Open the directory
        directory = options["directory"]

        for filename in os.listdir(directory):
            if filename.endswith(".json"):
                parts = filename.split("_")
                year = parts[1]
                issue = parts[2].split(".")[0]

                # Open json file
                with open(os.path.join(directory, filename), "r", encoding='utf-8') as f:
                    data = json.load(f)
                    issue_id = data["@id"]
                    title = data["label"]

                NdrCoreManifest.objects.create(identifier=f"{year}-{issue}",
                                               title=title,
                                               file=f"uploads/manifests/{filename}",
                                               manifest_group_id=1,
                                               order_value_1=year,
                                               order_value_2=issue,
                                               order_value_3=issue_id)
                self.stdout.write(self.style.SUCCESS(f"Created: {year}/{issue}: {title}"))
