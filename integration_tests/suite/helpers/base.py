# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import os

from wazo_admin_ui_test_helpers.asset_launching_test_case import AdminUIAssetLaunchingTestCase
from xivo_confd_test_helpers.helpers import setup_confd as setup_confd_helpers

from .pages.user import UserListPage

ASSET_ROOT = os.path.join(os.path.dirname(__file__), '..', '..', 'assets')


class IntegrationTest(AdminUIAssetLaunchingTestCase):

    assets_root = ASSET_ROOT

    @classmethod
    def setUpClass(cls):
        super(IntegrationTest, cls).setUpClass()
        cls.setup_helpers()

    @classmethod
    def setup_helpers(cls):
        setup_confd_helpers(host='localhost', port=cls.service_port('9486', 'confd'))

    @classmethod
    def setup_browser(cls):
        browser = super().setup_browser()
        browser.pages['users'] = UserListPage
        return browser
