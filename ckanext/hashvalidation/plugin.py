# encode: utf-8

import hashlib
import os

import ckan.plugins as p
import ckan.plugins.toolkit as tk
from ckan.lib.uploader import ResourceUpload as DefaultResourceUpload
from ckan.lib.helpers import flash_error


def get_file_hash(f):
    hash_md5 = hashlib.md5()
    # with fname as f:
    for chunk in iter(lambda: f.read(65536), b""):
        hash_md5.update(chunk)
    return hash_md5.hexdigest()


def hash_validator(key, data, errors, context):
    # print 'value >>>>>>>> : {}'.format(value)
    # print 'flatten_data >>>>>>>> : {}'.format(flatten_data.get(('resources', 0, 'file_hash_sum')))
    # print 'context >>>>>>>> : {}'.format(flatten_data[key])
    print "GET >>>>>>> {}".format(data.get(key, ), None)
    print "GET >>>>>>> {}".format(data.get((key[0], key[1], 'name',)), None)
    # resource_create = tk.get_action('resource_create')(context, data)
    # print 'ACTION {}'.format(resource_create)
    # if data[key] != 'xxx':
    #     raise tk.Invalid('Hash Invalid!')


class HashvalidationPlugin(p.SingletonPlugin, tk.DefaultDatasetForm):
    p.implements(p.IDatasetForm)
    p.implements(p.IConfigurer)
    p.implements(p.IUploader, inherit=True)

    def get_resource_uploader(self, data_dict):
        print 'UPLOAD >>>>>> {}'.format(data_dict)
        try:
            return ResourceUpload(data_dict)
        except ValueError:
            print 'ERROR <<<<<<<<<<<<<<<<<<<< '
            flash_error('File hash invalid')
        return None

    # def get_uploader(self, data_dict):
    #     print 'UPLOAD2 >>>>>> {}'.format(data_dict)
    #     return ResourceUpload(data_dict)

    def get_path(self, id):
        directory = self.get_directory(id)
        # filepath = os.path.join(
        #     directory, '{}_{}'.format(self.path_prefix, id[6:]))
        print 'PATH >>>>>>>>>>>>> {}'.format(directory)
        return directory

    def _modify_package_schema(self, schema):
        schema['resources'].update({'file_hash_sum': [hash_validator]})
        return schema

    def update_package_schema(self):
        print 'UPDATE >>>>>>>>>> '
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
        print 'MD >>>>>>>>>> {}'.format(get_file_hash(self.upload_file))
        self.file_hash = get_file_hash(self.upload_file)
        if self.file_hash != 'xxx':
            raise ValueError('Hash Invalid!')
            print 'FILE: {}'.format(self.file_name)

