"""Management command to update the config of a JS module UI element."""
import json
import os
from django.core.management.base import BaseCommand, CommandError
from ndr_core.models import NdrCoreUIElement


class Command(BaseCommand):
    """Update the js_module_config of a JS_MODULE UI element."""

    help = 'Updates the config of a JS module UI element'

    def add_arguments(self, parser):
        parser.add_argument(
            'element_name',
            nargs='?',
            type=str,
            help='Name (primary key) of the JS module UI element'
        )
        parser.add_argument(
            '--config',
            type=str,
            help='Path to a JSON file with the new config'
        )
        parser.add_argument(
            '--set',
            type=str,
            metavar='KEY=VALUE',
            action='append',
            dest='set_values',
            help='Set a top-level config key (e.g. --set options.api_url=/api/v1). '
                 'Dot notation sets nested keys. Can be repeated.'
        )
        parser.add_argument(
            '--show',
            action='store_true',
            help='Print the current config of the element'
        )
        parser.add_argument(
            '--list',
            action='store_true',
            help='List all JS module UI elements'
        )

    def handle(self, *args, **options):
        if options['list']:
            self._list_elements()
            return

        if not options['element_name']:
            raise CommandError('element_name is required (or use --list)')

        name = options['element_name']
        try:
            element = NdrCoreUIElement.objects.get(
                name=name,
                type=NdrCoreUIElement.UIElementType.JS_MODULE
            )
        except NdrCoreUIElement.DoesNotExist:
            raise CommandError(f'JS module UI element "{name}" not found')

        item = element.ndrcoreuielementitem_set.first()
        if item is None:
            raise CommandError(f'Element "{name}" has no items configured')

        if options['show']:
            self._show_config(element, item)
            return

        if not options['config'] and not options['set_values']:
            raise CommandError('Provide --config <file> or --set KEY=VALUE (or --show)')

        config = dict(item.js_module_config or {})

        if options['config']:
            config = self._load_config_file(options['config'])

        if options['set_values']:
            for kv in options['set_values']:
                if '=' not in kv:
                    raise CommandError(f'Invalid --set value "{kv}", expected KEY=VALUE')
                key, _, value = kv.partition('=')
                config = self._set_nested(config, key, value)

        item.js_module_config = config
        item.save()
        self.stdout.write(self.style.SUCCESS(f'Updated config for JS module "{name}"'))
        self._show_config(element, item)

    def _list_elements(self):
        elements = NdrCoreUIElement.objects.filter(
            type=NdrCoreUIElement.UIElementType.JS_MODULE
        ).order_by('name')
        if not elements:
            self.stdout.write(self.style.WARNING('No JS module UI elements found'))
            return
        for el in elements:
            item = el.ndrcoreuielementitem_set.first()
            constructor = (item.js_module_config or {}).get('constructor', '?') if item else '(no item)'
            self.stdout.write(f'  {el.name}  [{constructor}]')

    def _show_config(self, element, item):
        self.stdout.write(f'Element: {element.name}')
        self.stdout.write('Config:')
        self.stdout.write(json.dumps(item.js_module_config, indent=2))

    def _load_config_file(self, path):
        if not os.path.isfile(path):
            raise CommandError(f'File not found: {path}')
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise CommandError(f'Invalid JSON in {path}: {e}')
        if not isinstance(data, dict):
            raise CommandError('Config file must contain a JSON object')
        return data

    def _set_nested(self, config, key, value):
        """Set a potentially dot-notated key in config, auto-casting value to int/float/bool."""
        parts = key.split('.')
        node = config
        for part in parts[:-1]:
            if part not in node or not isinstance(node[part], dict):
                node[part] = {}
            node = node[part]
        node[parts[-1]] = self._cast(value)
        return config

    def _cast(self, value):
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'
        try:
            return int(value)
        except ValueError:
            pass
        try:
            return float(value)
        except ValueError:
            pass
        return value