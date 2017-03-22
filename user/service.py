# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from wazo_admin_ui.helpers.service import BaseConfdService


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
        if not user.get('fallbacks'):
            return

        self._confd.users(user['uuid']).update_fallbacks(user['fallbacks'])
