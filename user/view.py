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
        form.music_on_hold.choices = self._build_setted_choices_moh(resource.get('music_on_hold'))
        for form_line in form.lines:
            form_line.device.choices = self._build_setted_choices(form_line)
            form_line.context.choices = self._build_setted_choices_context(form_line)
            form_line.extensions[0].exten.choices = self._build_setted_choices_extension(form_line)
        return form

    def _build_setted_choices(self, line):
        if not line.device.data:
            return []
        text = line.device_mac.data if line.device_mac.data else line.device.data
        return [(line.device.data, text)]

    def _build_setted_choices_context(self, line):
        context = line.context.data if line.context.data != 'None' else ''
        return [(context, context)]

    def _build_setted_choices_extension(self, line):
        exten = line.extensions[0].exten.data if line.extensions[0].exten.data != 'None' else ''
        return [(exten, exten)]

    def _build_setted_choices_moh(self, moh):
        return [(moh, moh)]

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

            device_mac = self.service.get_device(line['device_id'])['mac'] if line['device_id'] else ''
            device = line['device_id'] if line['device_id'] else ''
            results.append({'protocol': protocol,
                            'name': name,
                            'device': device,
                            'device_mac': device_mac,
                            'position': line['position'],
                            'context': line['context'],
                            'id': line['id'],
                            'extensions': line['extensions'],
                            'endpoint_sip_id': endpoint_sip_id,
                            'endpoint_sccp_id': endpoint_sccp_id,
                            'endpoint_custom_id': endpoint_custom_id})
        return results

    def _map_form_to_resources(self, form, form_id=None):
        resource = form.to_dict()
        if form_id:
            resource['uuid'] = form_id

        lines = []
        for line in resource['lines']:
            result = {'id': int(line['id']) if line['id'] else None,
                      'context': line['context'],
                      'position': line['position']}

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

            if line['extensions'][0]['exten'] and line['context']:
                line['extensions'] = [{'exten': line['extensions'][0]['exten'],
                                       'context': line['context']}]

            if line['device']:
                line['device'] = {'id': line['device']}

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
