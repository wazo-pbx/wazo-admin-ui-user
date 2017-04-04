# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

from flask_menu.classy import classy_menu_item
from marshmallow import fields
from random import randint

from wazo_admin_ui.helpers.destination import FallbacksSchema
from wazo_admin_ui.helpers.classful import BaseView, BaseDestinationView
from wazo_admin_ui.helpers.mallow import BaseSchema, BaseAggregatorSchema, extract_form_fields

from .form import LineForm, UserForm


class LineSchema(BaseSchema):

    class Meta:
        fields = extract_form_fields(LineForm)


class UserSchema(BaseSchema):

    fallbacks = fields.Nested(FallbacksSchema)

    class Meta:
        fields = extract_form_fields(UserForm)


class AggregatorSchema(BaseAggregatorSchema):
    _main_resource = 'user'

    user = fields.Nested(UserSchema)
    lines = fields.List(fields.Nested(LineSchema))


class UserView(BaseView):

    form = UserForm
    resource = 'user'
    schema = AggregatorSchema
    ajax_listing = True

    @classy_menu_item('.users', 'Users', order=1, icon="user")
    def index(self):
        return super(UserView, self).index()

    def _map_resources_to_form(self, resources):
        data = self.schema().load(resources).data
        lines = self._build_lines(resources['user']['lines'])
        form = self.form(data=data['user'], lines=lines)
        return form

    def _build_lines(self, lines):
        results = []
        for line in lines:
            extension = context = extension_id = ''
            if line.get('extensions'):
                extension = line['extensions'][0]['exten']
                context = line['extensions'][0]['context']
                extension_id = line['extensions'][0]['id']

            name = protocol = 'undefined'
            endpoint_sip_id = endpoint_sccp_id = endpoint_custom_id = ''
            if line.get('endpoint_sip'):
                protocol = 'sip'
                name = line['endpoint_sip']['username']
                endpoint_sip_id = line['endpoint_sip']['id']
            elif line.get('endpoint_sccp'):
                protocol = 'sccp'
                name = extension
                endpoint_sccp_id = line['endpoint_sccp']['id']
            elif line.get('endpoint_custom'):
                protocol = 'custom'
                name = line['endpoint_custom']['interface']
                endpoint_custom_id = line['endpoint_custom']['id']

            results.append({'protocol': protocol,
                            'extension': extension,
                            'name': name,
                            'context': context,
                            'device': '12:34:56:78:9A',  # we dont have this information
                            'position': 1,  # we dont have this information
                            'line_id': line['id'],
                            'extension_id': extension_id,
                            'endpoint_sip_id': endpoint_sip_id,
                            'endpoint_sccp_id': endpoint_sccp_id,
                            'endpoint_custom_id': endpoint_custom_id})
        return results

    def _map_form_to_resources(self, form, form_id=None):
        data = self.schema(context={'resource_id': form_id}).dump(form).data
        lines = []
        for line in data['lines']:
            result = {'id': int(line['line_id']) if line['line_id'] else None,
                      'context': line['context'],
                      'position': line['position'],
                      'users': [{'uuid': form_id}]}

            if line['protocol'] == 'sip':
                result['endpoint_sip'] = {'id': line['endpoint_sip_id']}
            elif line['protocol'] == 'sccp':
                result['endpoint_sccp'] = {'id': line['endpoint_sccp_id']}
            elif line['protocol'] == 'custom':
                result['endpoint_custom'] = {'id': line['endpoint_custom_id'],
                                             'interface': str(randint(0, 99999999))}  # TODO: to improve ...

            if line['extension'] and line['context']:
                result['extensions'] = [{'id': line['extension_id'],
                                         'exten': line['extension'],
                                         'context': line['context']}]

            if line['device']:
                line['device'] = {'id': line['device']}

            lines.append(result)

        data['lines'] = lines
        return data


class UserDestinationView(BaseDestinationView):

    def list_json(self):
        return self._list_json('id')

    def uuid_list_json(self):
        return self._list_json('uuid')

    def _list_json(self, field_id):
        params = self._extract_params()
        users = self.service.list(**params)
        results = []
        for user in users['items']:
            if user.get('lastname'):
                text = '{} {}'.format(user['firstname'], user['lastname'])
            else:
                text = user['firstname']

            results.append({'id': user[field_id], 'text': text})

        return self._select2_response(results, users['total'], params)
