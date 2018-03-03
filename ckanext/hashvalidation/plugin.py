# encoding: utf-8

import os
import hashlib
import logging

import ckan.plugins as p
import ckan.plugins.toolkit as tk
from ckan.lib.uploader import ResourceUpload as DefaultResourceUpload
import ckan.lib.helpers as h


logger = logging.getLogger(__name__)


def get_file_hash(file_name):
    hash_md5 = hashlib.md5()
    with open(file_name, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


class HashValidationPlugin(p.SingletonPlugin):
    p.implements(p.IConfigurer)
    p.implements(p.IUploader, inherit=True)

    def update_package_schema(self):
        schema = super(HashValidationPlugin, self).update_package_schema()
        schema['resources'].update({'file_hash_sum': []})
        return schema

    # IUploder

    def get_resource_uploader(self, data_dict):
        return ResourceUpload(data_dict)

    # IConfigurer

    def update_config(self, config):
        tk.add_template_directory(config, 'templates')
        tk.add_public_directory(config, 'public')
        tk.add_resource('fanstatic', 'hashvalidator')


class ResourceUpload(DefaultResourceUpload):

    def __init__(self, resource):
        super(ResourceUpload, self).__init__(resource)
        self.resource = resource

    def upload(self, id, max_size=10):
        """
        Overloading the upload method to check the hash of the file. After downloading the file, we check the hash sum,
        if it does not match the users input, delete the file.
        :param id:
        :param max_size:
        :return:
        """
        super(ResourceUpload, self).upload(id)
        try:
            file_hash = get_file_hash(self.get_path(id))
        except OSError:
            logger.error('Сan not open file for hash sum checking!')
            h.flash_error(tk._('Trouble when file has sum checking. Try again.'))
            tk.redirect_to(controller='package', action='new_resource', id=self.resource.get('package_id'))
        if file_hash != self.resource.get('file_hash_sum'):
            try:
                os.remove(self.get_path(id))
            except OSError:
                logger.error('Сan not delete file!')
            h.flash_error(tk._('File hash sum invalid.'))
            tk.redirect_to(controller='package', action='new_resource', id=self.resource.get('package_id'))
            return None


