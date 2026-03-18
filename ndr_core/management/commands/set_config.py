"""Management command to update NDR Core configuration settings."""
from django.core.management.base import BaseCommand, CommandError
from ndr_core.models import NdrCoreValue


class Command(BaseCommand):
    """Update a single NDR Core configuration setting."""

    help = 'Updates a single NDR Core configuration setting value'

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            'setting_name',
            nargs='?',
            type=str,
            help='Name of the setting to create or update'
        )
        parser.add_argument(
            'value',
            nargs='?',
            type=str,
            help='New value for the setting'
        )
        parser.add_argument(
            '--list',
            action='store_true',
            help='List all available settings'
        )
        parser.add_argument(
            '--show',
            action='store_true',
            help='Show current value without updating'
        )
        parser.add_argument(
            '--update-only',
            action='store_true',
            help='Raise an error if the setting does not exist instead of creating it'
        )
        parser.add_argument(
            '--type',
            type=str,
            default='string',
            choices=['string', 'rich', 'integer', 'boolean', 'list', 'url', 'multi_list'],
            help='Value type for new settings (default: string)'
        )
        parser.add_argument(
            '--label',
            type=str,
            default=None,
            help='Human-readable label for new settings (defaults to setting_name)'
        )
        parser.add_argument(
            '--help-text',
            type=str,
            default='',
            help='Help text for new settings'
        )

    def handle(self, *args, **options):
        """Execute the command."""
        # Handle --list flag
        if options['list']:
            self._list_settings()
            return

        # Validate required arguments
        if not options['setting_name']:
            raise CommandError('setting_name is required (or use --list to see all settings)')

        setting_name = options['setting_name']

        # Handle --show flag
        if options['show']:
            self._show_setting(setting_name)
            return

        # Validate value argument for update operation
        if not options['value']:
            raise CommandError('value is required for update operation (or use --show to display current value)')

        new_value = options['value']

        # Perform create-or-update (or update-only if flag is set)
        self._set_setting(
            setting_name,
            new_value,
            update_only=options['update_only'],
            value_type=options['type'],
            label=options['label'],
            help_text=options['help_text'],
        )

    def _list_settings(self):
        """List all available settings."""
        settings = NdrCoreValue.objects.all().order_by('value_name')

        if not settings:
            self.stdout.write(self.style.WARNING('No settings found'))
            return

        self.stdout.write(self.style.SUCCESS(f'Found {settings.count()} settings:'))
        self.stdout.write('')

        for setting in settings:
            current_value = setting.value_value
            if len(current_value) > 50:
                current_value = current_value[:47] + '...'

            self.stdout.write(f'  {setting.value_name}')
            self.stdout.write(f'    Type: {setting.value_type}')
            self.stdout.write(f'    Current: {current_value}')
            self.stdout.write(f'    Label: {setting.value_label}')
            self.stdout.write('')

    def _show_setting(self, setting_name):
        """Display current value of a setting."""
        try:
            setting = NdrCoreValue.objects.get(value_name=setting_name)

            self.stdout.write(f'Setting: {setting.value_name}')
            self.stdout.write(f'Type: {setting.value_type}')
            self.stdout.write(f'Label: {setting.value_label}')
            self.stdout.write(f'Current value: {setting.value_value}')

            if setting.value_help_text:
                self.stdout.write(f'Help: {setting.value_help_text}')

            if setting.value_options:
                self.stdout.write(f'Options: {setting.value_options}')

        except NdrCoreValue.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Setting "{setting_name}" does not exist'))
            raise CommandError(f'Setting "{setting_name}" not found')

    def _set_setting(self, setting_name, new_value, update_only=False, value_type='string', label=None, help_text=''):
        """Create or update a setting value."""
        try:
            setting = NdrCoreValue.objects.get(value_name=setting_name)
            old_value = setting.value_value
            validated_value = self._validate_value(setting, new_value)
            setting.value_value = validated_value
            setting.save()
            self.stdout.write(
                self.style.SUCCESS(f'Updated {setting_name}: "{old_value}" -> "{validated_value}"')
            )
        except NdrCoreValue.DoesNotExist:
            if update_only:
                self.stdout.write(self.style.ERROR(f'Setting "{setting_name}" does not exist'))
                raise CommandError(f'Setting "{setting_name}" not found')
            # Create new setting
            setting = NdrCoreValue(
                value_name=setting_name,
                value_type=value_type,
                value_label=label if label is not None else setting_name,
                value_help_text=help_text,
                value_value=new_value,
                is_user_value=True,
            )
            setting.save()
            self.stdout.write(
                self.style.SUCCESS(f'Created {setting_name} ({value_type}): "{new_value}"')
            )
        except ValueError as e:
            self.stdout.write(self.style.ERROR(f'Invalid value: {str(e)}'))
            raise CommandError(str(e))

    def _validate_value(self, setting, value):
        """Validate and convert value based on setting type."""
        value_type = setting.value_type

        if value_type == NdrCoreValue.ValueType.BOOLEAN:
            return self._parse_boolean(value)

        elif value_type == NdrCoreValue.ValueType.INTEGER:
            return self._parse_integer(value)

        elif value_type == NdrCoreValue.ValueType.MULTI_LIST:
            # For multi-list, ensure comma-separated format
            # Remove spaces around commas for consistency
            return ','.join([item.strip() for item in value.split(',')])

        elif value_type == NdrCoreValue.ValueType.LIST:
            # For single list, validate against options if available
            if setting.value_options:
                valid_keys = [key for key, _ in setting.get_options()]
                if value not in valid_keys:
                    raise ValueError(
                        f'Invalid value "{value}". Valid options: {", ".join(valid_keys)}'
                    )

        # For STRING, RICH_STRING, URL, return as-is
        return value

    def _parse_boolean(self, value):
        """Parse boolean value from string."""
        value_lower = value.lower()

        if value_lower in ['true', 'yes', '1', 'on']:
            return 'true'
        elif value_lower in ['false', 'no', '0', 'off']:
            return 'false'
        else:
            raise ValueError(
                f'Invalid boolean value "{value}". Use: true/false, yes/no, 1/0, on/off'
            )

    def _parse_integer(self, value):
        """Parse integer value from string."""
        try:
            int(value)
            return value
        except ValueError:
            raise ValueError(f'Invalid integer value "{value}"')
