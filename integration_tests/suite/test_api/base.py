# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import os

from xivo_test_helpers.admin_ui.asset_launching_test_case import AdminUIAssetLaunchingTestCase
from xivo_test_helpers.confd import provd

from .pages.user import UserListPage

ASSET_ROOT = os.path.join(os.path.dirname(__file__), '..', '..', 'assets')


class IntegrationTest(AdminUIAssetLaunchingTestCase):

    assets_root = ASSET_ROOT

    @classmethod
    def setUpClass(cls):
        super(IntegrationTest, cls).setUpClass()
        provd.reset()

    @classmethod
    def setup_browser(cls):
        browser = AdminUIAssetLaunchingTestCase.setup_browser()
        browser.pages['users'] = UserListPage
        return browser
