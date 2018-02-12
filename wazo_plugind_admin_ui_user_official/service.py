# Copyright 2017-2018 The Wazo Authors  (see the AUTHORS file)
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

    def list_funckeys(self, user_uuid):
        return confd.users(user_uuid).list_funckeys()

    def is_webrtc(self, endpoint_id):
        endpoint_sip = confd.endpoints_sip.get(endpoint_id)
        if ['transport', 'wss'] in endpoint_sip['options']:
            return True
        return False

    def create(self, user):
        user['uuid'] = super(UserService, self).create(user)['uuid']
        if user.get('username') and user.get('password'):
            confd.users(user['uuid']).update_cti_profile(user['cti_profile'])
        self._create_user_lines(user)

    def update(self, user):
        super(UserService, self).update(user)

        existing_user = confd.users.get(user)

        if user.get('fallbacks'):
            confd.users(user['uuid']).update_fallbacks(user['fallbacks'])

        if user.get('services'):
            confd.users(user['uuid']).update_services(user['services'])

        if user.get('forwards'):
            confd.users(user['uuid']).update_forwards(user['forwards'])

        if user.get('schedules'):
            self._update_schedules(existing_user, user)

        confd.users(user['uuid']).update_cti_profile(user['cti_profile'])
        self._update_voicemail(existing_user, user)
        self._update_user_lines(existing_user, user)

        if 'groups' in user and user.get('lines'):
            confd.users(user).update_groups(user['groups'])

        if user.get('funckeys'):
            confd.users(user['uuid']).update_funckeys(user['funckeys'])

    def delete(self, user_uuid):
        user = confd.users.get(user_uuid)
        self._delete_user_associations(user)
        confd.users.delete(user_uuid)

    def _delete_user_associations(self, user):
        if user.get('voicemail'):
            confd.users(user['uuid']).remove_voicemail()

        lines = user.get('lines', [])
        for line in lines:
            device_id = confd.lines.get(line['id'])['device_id']
            if device_id:
                confd.lines(line['id']).remove_device(device_id)
            confd.lines.delete(line)

    def _create_user_lines(self, user):
        lines = user.get('lines', [])

        for line in lines:
            if not line.get('id'):
                line = self._create_line_and_associations(line)
            confd.users(user).add_line(line)

    def _update_schedules(self, existing_user, user):
        if existing_user['schedules']:
            schedule_id = existing_user['schedules'][0]['id']
            confd.users(user).remove_schedule(schedule_id)
        if user['schedules'][0].get('id'):
            confd.users(user).add_schedule(user['schedules'][0])

    def _update_voicemail(self, existing_user, user):
        existing_voicemail_id = existing_user['voicemail'].get('id') if existing_user['voicemail'] else None
        voicemail_id = int(user['voicemail']['id']) if user['voicemail'].get('id') else None

        if existing_voicemail_id == voicemail_id:
            return

        if existing_voicemail_id:
            confd.users(user).remove_voicemail()

        if voicemail_id:
            confd.users(user).add_voicemail(user['voicemail'])

    def _update_user_lines(self, existing_user, user):
        lines = user.get('lines', [])
        line_ids = set([l.get('id') for l in lines])
        existing_lines = existing_user['lines']
        existing_line_ids = set([l['id'] for l in existing_lines])

        line_ids_to_remove = existing_line_ids - line_ids
        for line_id in line_ids_to_remove:
            device_id = confd.lines.get(line_id)['device_id']
            if device_id:
                confd.lines(line_id).remove_device(device_id)
            confd.lines.delete(line_id)

        for line in lines:
            if line.get('id'):
                self._update_line_and_associations(line)
                self._update_device_association(line['id'], line.get('device_id'))
            else:
                line = self._create_line_and_associations(line)
                if line.get('device_id'):
                    confd.lines(line).add_device(line['device_id'])

        if line_ids != existing_line_ids or self._get_first_line_id(lines) != self._get_first_line_id(existing_lines):
            confd.users(user).update_lines(lines)

    def _get_first_line_id(self, lines):
        for line in lines:
            return line['id']
        return None

    def _update_device_association(self, line_id, device_id):
        existing_device_id = confd.lines.get(line_id)['device_id']

        if not device_id and not existing_device_id:
            return
        if device_id == existing_device_id:
            return

        if not device_id and existing_device_id:
            confd.lines(line_id).remove_device(existing_device_id)
        elif device_id and not existing_device_id:
            confd.lines(line_id).add_device(device_id)
        elif device_id != existing_device_id:
            confd.lines(line_id).remove_device(existing_device_id)
            confd.lines(line_id).add_device(device_id)

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

        return line

    def _update_line_and_associations(self, line):
        if line.get('endpoint_sip'):
            # If we move from SIP to WEBRTC
            if 'options' in line['endpoint_sip']:
                self._update_endoint_sip_webrtc(line['endpoint_sip'])
            confd.endpoints_sip.update(line['endpoint_sip'])

        extensions = line.get('extensions', [])
        if extensions and extensions[0].get('id'):
            existing_extension = confd.extensions.get(extensions[0])
            if self._is_extension_has_changed(extensions[0], existing_extension):
                if self._is_extension_associated_with_other_lines(existing_extension):
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

    def _update_endoint_sip_webrtc(self, endpoint_sip):
        existing_endpoint_sip_options = confd.endpoints_sip.get(endpoint_sip)['options']
        merged_endpoint_sip_options_dict = {**dict(existing_endpoint_sip_options), **dict(endpoint_sip['options'])}
        endpoint_sip['options'] = [(k, v) for k, v in merged_endpoint_sip_options_dict.items()]

    def _is_extension_associated_with_other_lines(self, extension):
        if len(extension['lines']) > 1:
            return True
        return False

    def _is_extension_has_changed(self, extension, existing_extension):
        if existing_extension['exten'] == extension['exten'] and \
           existing_extension['context'] == extension['context']:
            return False
        return True

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

    def get_first_internal_context(self):
        result = confd.contexts.list(type='internal', limit=1, direction='asc', order='id')
        for context in result['items']:
            return context

    def get_context(self, context):
        result = confd.contexts.list(name=context)
        for context in result['items']:
            return context

    def get_cti_profile(self, id):
        return confd.cti_profiles.get(id)


class CtiService(BaseConfdService):

    def list(self):
        return confd.cti_profiles.list()
