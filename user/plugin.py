# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from flask_menu.classy import register_flaskview

from wazo_admin_ui.helpers.plugin import create_blueprint
from wazo_admin_ui.helpers.destination import register_destination_form, register_listing_url

from .service import UserService
from .view import UserView, UserDestinationView
from .form import UserDestinationForm

user = create_blueprint('user', __name__)


class Plugin(object):

    def load(self, dependencies):
        core = dependencies['flask']

        UserView.service = UserService()
        UserView.register(user, route_base='/users')
        register_flaskview(user, UserView)

        UserDestinationView.service = UserService()
        UserDestinationView.register(user, route_base='/users_listing')

        register_destination_form('user', 'User', UserDestinationForm)

        register_listing_url('user', 'user.UserDestinationView:list_json')
        register_listing_url('uuid_user', 'user.UserDestinationView:uuid_list_json')

        core.register_blueprint(user)
