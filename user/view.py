# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from __future__ import unicode_literals

from flask_menu.classy import classy_menu_item
from marshmallow import fields

from wazo_admin_ui.helpers.classful import BaseView
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
