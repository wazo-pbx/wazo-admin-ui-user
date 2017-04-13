# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import logging

from wazo_admin_ui.helpers.service import BaseConfdService
from wazo_admin_ui.helpers.confd import confd

logger = logging.getLogger(__name__)


class UserService(BaseConfdService):

    resource_confd = 'users'

    def list(self, limit=None, order=None, direction=None, offset=None, search=None):
        return confd.users.list(view='summary',
                                search=search,
                                order=order,
                                limit=limit,
                                direction=direction,
                                offset=offset)

    def get_line(self, line_id):
        return confd.lines.get(line_id)

    def get_device(self, device_id):
        return confd.devices.get(device_id)

    def get_endpoint(self, endpoint_id):
        return confd.endpoints_sip.get(endpoint_id)

    def is_webrtc(self, endpoint_id):
        endpoint = self.get_endpoint(endpoint_id)
        for option in endpoint['options']:
            if option[0] == 'transport':
                if option[1] == 'wss':
                    return True
        return False

    def update(self, resource):
        super(UserService, self).update(resource)

        user = resource
        if user.get('fallbacks'):
            confd.users(user['uuid']).update_fallbacks(user['fallbacks'])

        self._update_user_lines(user)

    def _create_user_lines(self, user):
        lines = user.get('lines', [])

        for line in lines:
            if not line.get('id'):
                line = self._create_line_and_associations(line)
            confd.users(user).add_line(line)

    def _update_user_lines(self, user):
        lines = user.get('lines', [])
        line_ids = set([l.get('id') for l in lines])
        existing_lines = confd.users.get(user['uuid'])['lines']
        existing_line_ids = set([l['id'] for l in existing_lines])

        line_ids_to_remove = existing_line_ids - line_ids
        for line_id in line_ids_to_remove:
            self._delete_line_and_associations(line_id)
            existing_line_ids.remove(line_id)

        # Handle case of main_line
        existing_lines = [l for l in existing_lines if l['id'] not in line_ids_to_remove]
        if lines and existing_lines and lines[0]['id'] != existing_lines[0]['id']:
            for line_id in existing_line_ids:
                # TODO: Dissociate device first
                confd.users(user).remove_line(line_id)
            existing_line_ids = set([])

        for line in lines:
            if line.get('id'):
                self._update_line_and_associations(line)
                if line.get('id') not in existing_line_ids:
                    confd.users(user).add_line(line)
            else:
                line = self._create_line_and_associations(line)
                confd.users(user).add_line(line)

    def _delete_line_and_associations(self, line_id):
        line = confd.lines.get(line_id)

        for extension in line.get('extensions', []):
            confd.lines(line).remove_extension(extension)
            confd.extensions.delete(extension)

        confd.lines.delete(line)

    def _create_line_and_associations(self, line):
        line['id'] = confd.lines.create(line)['id']

        if 'endpoint_sip' in line:
            endpoint_sip = confd.endpoints_sip.create(line['endpoint_sip'])
            if endpoint_sip:
                confd.lines(line).add_endpoint_sip(endpoint_sip)
        elif 'endpoint_sccp' in line:
            endpoint_sccp = confd.endpoints_sccp.create(line['endpoint_sccp'])
            if endpoint_sccp:
                confd.lines(line).add_endpoint_sccp(endpoint_sccp)
        elif 'endpoint_custom' in line:
            endpoint_custom = confd.endpoints_custom.create(line['endpoint_custom'])
            if endpoint_custom:
                confd.lines(line).add_endpoint_custom(endpoint_custom)
        else:
            logger.debug('No endpoint found for line: %s', line)
            return line

        if line.get('extensions'):
            self._create_or_associate_extension(line, line['extensions'][0])

        # TODO: create device

        return line

    def _update_line_and_associations(self, line):
        if line.get('endpoint_sip'):
            # If we move from SIP to WEBRTC
            confd.endpoints_sip.update(line['endpoint_sip'])

        # TODO: update device

        extensions = line.get('extensions', [])
        if extensions and extensions[0].get('id'):
            if self._is_extension_associated_with_other_lines(extensions[0]):
                confd.lines(line).remove_extension(extensions[0])
                extension_created = confd.extensions.create(extensions[0])
                confd.lines(line).add_extension(extension_created)
            else:
                confd.extensions.update(extensions[0])

        elif extensions:
            self._create_or_associate_extension(line, extensions[0])

        else:
            existing_extensions = confd.lines.get(line['id']).get('extensions')
            if existing_extensions:
                confd.lines(line).remove_extension(existing_extensions[0])
                confd.extensions.delete(existing_extensions[0])

        confd.lines.update(line)

    def _is_extension_associated_with_other_lines(self, extension):
        extension = self._get_first_existing_extension(extension)
        if len(extension['lines']) > 1:
            return True
        return False

    def _create_or_associate_extension(self, line, extension):
        existing_extension = self._get_first_existing_extension(extension)

        if not existing_extension:
            existing_extension = confd.extensions.create(extension)

        if existing_extension:
            confd.lines(line).add_extension(existing_extension)

    def _get_first_existing_extension(self, extension):
        items = confd.extensions.list(exten=extension['exten'],
                                      context=extension['context'])['items']
        return items[0] if items else None
