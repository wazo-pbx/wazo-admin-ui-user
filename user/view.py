# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

from flask_menu.classy import classy_menu_item
from marshmallow import fields

from wazo_admin_ui.helpers.classful import BaseView, BaseDestinationView
from wazo_admin_ui.helpers.mallow import BaseSchema, BaseAggregatorSchema, extract_form_fields

from .form import UserForm


class UserSchema(BaseSchema):

    class Meta:
        fields = extract_form_fields(UserForm)


class AggregatorSchema(BaseAggregatorSchema):
    _main_resource = 'user'

    user = fields.Nested(UserSchema)


class UserView(BaseView):

    form = UserForm
    resource = 'user'
    schema = AggregatorSchema
    ajax_listing = True

    @classy_menu_item('.users', 'Users', order=1, icon="user")
    def index(self):
        return super(UserView, self).index()


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
