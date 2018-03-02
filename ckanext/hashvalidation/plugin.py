# encode: utf-8

import hashlib
import os

import ckan.plugins as p
import ckan.plugins.toolkit as tk
from ckan.lib.uploader import ResourceUpload as DefaultResourceUpload
from ckan.lib.helpers import flash_error


def get_file_hash(file_name):
    hash_md5 = hashlib.md5()
    with open(file_name, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


class HashvalidationPlugin(p.SingletonPlugin, tk.DefaultDatasetForm):
    p.implements(p.IDatasetForm)
    p.implements(p.IConfigurer)
    p.implements(p.IUploader, inherit=True)

    def get_resource_uploader(self, data_dict):
        return ResourceUpload(data_dict)

    def _modify_package_schema(self, schema):
        schema['resources'].update({'file_hash_sum': []})
        return schema

    def update_package_schema(self):
        schema = super(HashvalidationPlugin, self).update_package_schema()
        schema = self._modify_package_schema(schema)
        return schema

    def is_fallback(self):
        # Return True to register this plugin as the default handler for
        # package types not handled by any other IDatasetForm plugin.
        return True

    def package_types(self):
        # This plugin doesn't handle any special package types, it just
        # registers itself as the default (above).
        return []

    # update config
    def update_config(self, config):
        # Add this plugin's templates dir to CKAN's extra_template_paths, so
        # that CKAN will use this plugin's custom templates.
        tk.add_template_directory(config, 'templates')


class ResourceUpload(DefaultResourceUpload):

    def __init__(self, resource):
        super(ResourceUpload, self).__init__(resource)
        self.resource = resource

    def upload(self, id, max_size=10):
        super(ResourceUpload, self).upload(id)
        file_hash = get_file_hash(self.get_path(id))
        if file_hash != self.resource.get('file_hash_sum'):
            try:
                os.remove(self.get_path(id))
            except IOError:
                pass
            except OSError:
                pass
            flash_error('File hash invalid')
            tk.redirect_to(controller='dataset_resources', id=self.resource.get('package_id'))
            return None


