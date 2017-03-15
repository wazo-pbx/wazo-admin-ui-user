# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from flask_menu.classy import register_flaskview

from wazo_admin_ui.helpers.plugin import create_blueprint
from wazo_admin_ui.core.destination import destination_blueprint

from .service import UserService
from .view import UserView, UserDestinationView

user = create_blueprint('user', __name__)


class Plugin(object):

    def load(self, dependencies):
        core = dependencies['flask']
        config = dependencies['config']

        UserView.service = UserService(config['confd'])
        UserView.register(user, route_base='/users')
        register_flaskview(user, UserView)

        UserDestinationView.service = UserService(config['confd'])
        UserDestinationView.register(destination_blueprint, route_base='/user_destination')

        core.register_blueprint(user)
