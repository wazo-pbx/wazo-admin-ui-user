# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import logging

from wazo_admin_ui.helpers.service import BaseConfdService

logger = logging.getLogger(__name__)


class UserService(BaseConfdService):

    resource_name = 'user'
    resource_confd = 'users'

    def list(self, limit=None, order=None, direction=None, offset=None, search=None):
        return self._confd.users.list(view='summary',
                                      search=search,
                                      order=order,
                                      limit=limit,
                                      direction=direction,
                                      offset=offset)

    def update(self, resources):
        super(UserService, self).update(resources)

        user = resources.get('user', {})
        if user.get('fallbacks'):
            self._confd.users(user['uuid']).update_fallbacks(user['fallbacks'])

        lines = resources.get('lines', [])
        line_ids = set([l.get('id') for l in lines])
        existing_lines = self._confd.users.get(user['uuid'])['lines']
        existing_line_ids = set([l['id'] for l in existing_lines])

        line_ids_to_remove = existing_line_ids - line_ids
        for line_id in line_ids_to_remove:
            # TODO: Dissociate device first
            self._confd.users(user).remove_line(line_id)
            self._delete_line_and_associations(line_id)
            existing_line_ids.remove(line_id)

        # Handle case of main_line
        existing_lines = [l for l in existing_lines if l['id'] not in line_ids_to_remove]
        if lines and existing_lines and lines[0]['id'] != existing_lines[0]['id']:
            for line_id in existing_line_ids:
                # TODO: Dissociate device first
                self._confd.users(user).remove_line(line_id)
            existing_line_ids = set([])

        for line in lines:
            if not line.get('id'):
                line = self._create_line_and_associations(line)
                self._confd.users(user).add_line(line)
                continue

            self._update_line_and_associations(line)
            if line.get('id') not in existing_line_ids:
                self._confd.users(user).add_line(line)

    def _delete_line_and_associations(self, line_id):
        line = self._confd.lines.get(line_id)

        # TODO: delete device

        for extension in line.get('extensions', []):
            self._confd.lines(line).remove_extension(extension)
            self._confd.extensions.delete(extension)

        if line.get('endpoint_sip'):
            self._confd.lines(line).remove_endpoint_sip(line['endpoint_sip'])
            self._confd.endpoints_sip.delete(line['endpoint_sip'])
        elif line.get('endpoint_sccp'):
            self._confd.lines(line).remove_endpoint_sccp(line['endpoint_sccp'])
            self._confd.endpoints_sccp.delete(line['endpoint_sccp'])
        elif line.get('endpoint_custom'):
            self._confd.lines(line).remove_endpoint_custom(line['endpoint_custom'])
            self._confd.endpoints_custom.delete(line['endpoint_custom'])

        self._confd.lines.delete(line)

    def _create_line_and_associations(self, line):
        line['id'] = self._confd.lines.create(line)['id']

        if 'endpoint_sip' in line:
            endpoint_sip = self._confd.endpoints_sip.create(line['endpoint_sip'])
            if endpoint_sip:
                self._confd.lines(line).add_endpoint_sip(endpoint_sip)
        elif 'endpoint_sccp' in line:
            endpoint_sccp = self._confd.endpoints_sccp.create(line['endpoint_sccp'])
            if endpoint_sccp:
                self._confd.lines(line).add_endpoint_sccp(endpoint_sccp)
        elif 'endpoint_custom' in line:
            endpoint_custom = self._confd.endpoints_custom.create(line['endpoint_custom'])
            if endpoint_custom:
                self._confd.lines(line).add_endpoint_custom(endpoint_custom)
        else:
            logger.debug('No endpoint found for line: %s', line)
            return line

        if line.get('extensions'):
            extension = self._confd.extensions.create(line['extensions'][0])
            if extension:
                self._confd.lines(line).add_extension(extension)

        # TODO: create device

        return line

    def _update_line_and_associations(self, line):
        if line.get('endpoint_sip'):
            # If we move from SIP to WEBRTC
            self._confd.endpoints_sip.update(line['endpoint_sip'])

        # TODO: update device

        extension = line.get('extensions', [{}])[0]
        if extension.get('id'):
            self._confd.extensions.update(extension)

        elif extension:
            extension = self._confd.extensions.create(extension)
            if extension:
                self._confd.lines(line).add_extension(extension)

        else:
            existing_extensions = self._confd.lines.get(line['id']).get('extensions')
            if existing_extensions:
                self._confd.lines(line).remove_extension(existing_extensions[0])
                self._confd.extensions.delete(existing_extensions[0])

        self._confd.lines.update(line)
