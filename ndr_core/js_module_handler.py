"""
JavaScript Module Package Handler

Handles extraction and installation of JS module packages.
Uses Django's storage API for cloud compatibility.
"""

import json
import zipfile
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.exceptions import ValidationError


def extract_module_package(package_file, element_name, module_name_hint=''):
    """
    Extract module package to Django storage.

    Expected zip structure:
        config.json          # Module metadata
        static/              # JS, CSS files
            module.js
            module.css
        media/               # Images, data files
            images/
                img001.jpg
                img002.jpg
            data.json

    Args:
        package_file: UploadedFile object
        element_name: UI element name (for storage paths)
        module_name_hint: Suggested module name (can be overridden by config.json)

    Returns:
        dict: Extracted configuration with 'name' and 'config' keys

    Raises:
        ValidationError: If package structure is invalid
    """

    # Read zip file
    try:
        zip_data = package_file.read()
        zip_file = zipfile.ZipFile(BytesIO(zip_data))
    except zipfile.BadZipFile:
        raise ValidationError("Invalid zip file format")

    # Read and validate config.json
    try:
        config_data = zip_file.read('config.json').decode('utf-8')
        config = json.loads(config_data)
    except KeyError:
        raise ValidationError("Package must contain config.json at root level")
    except json.JSONDecodeError as e:
        raise ValidationError(f"Invalid JSON in config.json: {e}")
    except UnicodeDecodeError:
        raise ValidationError("config.json must be UTF-8 encoded")

    # Validate config structure
    if not isinstance(config, dict):
        raise ValidationError("config.json must be a JSON object")

    module_name = config.get('name', module_name_hint or element_name)

    # Define storage paths - everything goes to media/js_modules/{element_name}/
    module_base = f'js_modules/{element_name}/'
    media_base = f'{module_base}media/'

    # Extract files - separate JS from CSS
    extracted_files = {'scripts': [], 'styles': [], 'media': []}

    for file_info in zip_file.filelist:
        # Skip directories and config.json
        if file_info.is_dir() or file_info.filename == 'config.json':
            continue

        file_path = file_info.filename

        if file_path.startswith('static/'):
            # Extract JS/CSS to module base (NOT nested static/)
            rel_path = file_path[7:]  # Remove 'static/' prefix
            if rel_path:
                storage_path = module_base + rel_path  # Direct to js_modules/{element}/
                content = zip_file.read(file_path)

                # Save to storage
                if default_storage.exists(storage_path):
                    default_storage.delete(storage_path)
                default_storage.save(storage_path, ContentFile(content))

                # Separate JS files from CSS files
                if rel_path.endswith('.js'):
                    extracted_files['scripts'].append(storage_path)
                elif rel_path.endswith('.css'):
                    extracted_files['styles'].append(storage_path)

        elif file_path.startswith('media/'):
            # Extract media to media subfolder
            rel_path = file_path[6:]  # Remove 'media/' prefix
            if rel_path:
                storage_path = media_base + rel_path  # To js_modules/{element}/media/
                content = zip_file.read(file_path)

                # Save to storage
                if default_storage.exists(storage_path):
                    default_storage.delete(storage_path)
                default_storage.save(storage_path, ContentFile(content))

                extracted_files['media'].append(storage_path)

    zip_file.close()

    # Build final configuration
    module_config = {
        'scripts': config.get('scripts', []),
        'styles': config.get('styles', []),
        'constructor': config.get('constructor', module_name.replace('-', '_').title()),
        'options': config.get('options', {})
    }

    # Build paths that work with /media/ URL prefix
    # Add extracted JS files to scripts array
    if extracted_files['scripts']:
        extracted_scripts = [f'/media/{path}' for path in extracted_files['scripts']]
        module_config['scripts'].extend(extracted_scripts)

    # Add extracted CSS files to styles array
    if extracted_files['styles']:
        extracted_styles = [f'/media/{path}' for path in extracted_files['styles']]
        module_config['styles'].extend(extracted_styles)

    if extracted_files['media']:
        module_config['extracted_media'] = extracted_files['media']
        # Set media base path for relative references
        module_config['options']['mediaBasePath'] = f'/media/{media_base}'

    return {
        'name': module_name,
        'config': module_config,
        'extracted_files': extracted_files
    }


def cleanup_module_files(element_name):
    """
    Clean up extracted module files from storage.

    Args:
        element_name: UI element name
    """
    module_base = f'js_modules/{element_name}/'

    # Delete all files in module directory
    def cleanup_dir(dir_path):
        """Recursively delete directory contents."""
        try:
            dirs, files = default_storage.listdir(dir_path)
            for file_name in files:
                default_storage.delete(f'{dir_path}{file_name}')
            for dir_name in dirs:
                cleanup_dir(f'{dir_path}{dir_name}/')
        except Exception:
            pass  # Directory might not exist

    cleanup_dir(module_base)
