# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

from flask import request, jsonify
from flask_menu.classy import classy_menu_item
from random import randint

from wazo_admin_ui.helpers.classful import IndexAjaxViewMixin, BaseView, LoginRequiredView
from wazo_admin_ui.helpers.classful import extract_select2_params, build_select2_response

from .form import UserForm


class UserView(IndexAjaxViewMixin, BaseView):

    form = UserForm
    resource = 'user'

    @classy_menu_item('.users', 'Users', order=1, icon="user")
    def index(self):
        return super(UserView, self).index()

    def _map_resources_to_form(self, resource):
        resource_lines = [self.service.get_line(line['id']) for line in resource['lines']]
        lines = self._build_lines(resource_lines)
        form = self.form(data=resource, lines=lines)
        return form

    def _populate_form(self, form):
        form.cti_profile.form.id.choices = self._build_setted_choices_cti_profile(form)
        form.music_on_hold.choices = self._build_setted_choices_moh(form)
        for form_line in form.lines:
            form_line.device.choices = self._build_setted_choices_device(form_line)
            form_line.context.choices = self._build_setted_choices_context(form_line)
            for form_extension in form_line.extensions:
                form_extension.exten.choices = self._build_setted_choices_extension(form_extension)
        return form

    def _build_setted_choices_device(self, line):
        if not line.device.data or line.device.data == 'None':
            return []
        device_mac = self.service.get_device(line.device.data)['mac']
        text = device_mac if device_mac else line.device.data
        return [(line.device.data, text)]

    def _build_setted_choices_context(self, line):
        if not line.context.data or line.context.data == 'None':
            return []
        return [(line.context.data, line.context.data)]

    def _build_setted_choices_extension(self, extension):
        if not extension.exten.data or extension.exten.data == 'None':
            return []
        return [(extension.exten.data, extension.exten.data)]

    def _build_setted_choices_moh(self, user):
        if not user.music_on_hold.data or user.music_on_hold.data == 'None':
            return []
        return [(user.music_on_hold.data, user.music_on_hold.data)]

    def _build_setted_choices_cti_profile(self, user):
        if not user.cti_profile.form.id.data or user.cti_profile.form.id.data == 'None':
            return []
        return [(user.cti_profile.form.id.data, user.cti_profile.form.name.data)]

    def _build_lines(self, lines):
        results = []
        for line in lines:
            name = protocol = 'undefined'
            endpoint_sip_id = endpoint_sccp_id = endpoint_custom_id = ''
            if line.get('endpoint_sip'):
                protocol = 'sip'
                name = line['endpoint_sip']['username']
                endpoint_sip_id = line['endpoint_sip']['id']
                if self.service.is_webrtc(endpoint_sip_id):
                    protocol = 'webrtc'
            elif line.get('endpoint_sccp'):
                protocol = 'sccp'
                name = line['extensions'][0]['exten'] if line['extensions'] else ''
                endpoint_sccp_id = line['endpoint_sccp']['id']
            elif line.get('endpoint_custom'):
                protocol = 'custom'
                name = line['endpoint_custom']['interface']
                endpoint_custom_id = line['endpoint_custom']['id']

            device = line['device_id'] if line['device_id'] else ''
            results.append({'protocol': protocol,
                            'name': name,
                            'device': device,
                            'position': line['position'],
                            'context': line['context'],
                            'id': line['id'],
                            'extensions': line['extensions'],
                            'endpoint_sip_id': endpoint_sip_id,
                            'endpoint_sccp_id': endpoint_sccp_id,
                            'endpoint_custom_id': endpoint_custom_id})
        return results

    def _map_form_to_resources_post(self, form):
        form.username.raw_data = form.email.raw_data
        form.username.data = form.email.data
        return self._map_form_to_resources(form)

    def _map_form_to_resources(self, form, form_id=None):
        resource = form.to_dict()
        if form_id:
            resource['uuid'] = form_id

        lines = []
        for line in resource['lines']:
            if request.method == 'POST' and not line.get('context'):
                continue
            result = {'id': int(line['id']) if line['id'] else None,
                      'context': line.get('context'),
                      'position': line['position'],
                      'device_id': line.get('device')}

            if line['protocol'] == 'sip':
                result['endpoint_sip'] = {'id': line['endpoint_sip_id']}
            elif line['protocol'] == 'webrtc':
                result['endpoint_sip'] = {'id': line['endpoint_sip_id'],
                                          'options': [
                                              ('transport', 'wss'),
                                              ('directmedia', 'no'),
                                              ('encryption', 'yes'),
                                              ('dtlsenable', 'yes'),
                                              ('dtlsverify', 'no'),
                                              ('dtlscertfile', '/usr/share/xivo-certs/server.crt'),
                                              ('dtlsprivatekey', '/usr/share/xivo-certs/server.key'),
                                              ('dtlssetup', 'actpass'),
                                              ('force_avp', 'yes'),
                                              ('avpf', 'yes'),
                                              ('nat', 'force_rport,comedia'),
                                              ('icesupport', 'yes')
                                          ]}
            elif line['protocol'] == 'sccp':
                result['endpoint_sccp'] = {'id': line['endpoint_sccp_id']}
            elif line['protocol'] == 'custom':
                result['endpoint_custom'] = {'id': line['endpoint_custom_id'],
                                             'interface': str(randint(0, 99999999))}  # TODO: to improve ...

            if line['extensions'][0].get('exten') and line.get('context'):
                result['extensions'] = [{'id': line['extensions'][0]['id'],
                                         'exten': line['extensions'][0]['exten'],
                                         'context': line['context']}]

            lines.append(result)

        resource['lines'] = lines
        return resource

    def _map_resources_to_form_errors(self, form, resources):
        form.populate_errors(resources.get('user', {}))
        return form


class UserDestinationView(LoginRequiredView):

    def list_json(self):
        return self._list_json('id')

    def uuid_list_json(self):
        return self._list_json('uuid')

    def _list_json(self, field_id):
        params = extract_select2_params(request.args)
        users = self.service.list(**params)
        results = []
        for user in users['items']:
            if user.get('lastname'):
                text = '{} {}'.format(user['firstname'], user['lastname'])
            else:
                text = user['firstname']

            results.append({'id': user[field_id], 'text': text})

        return jsonify(build_select2_response(results, users['total'], params))
