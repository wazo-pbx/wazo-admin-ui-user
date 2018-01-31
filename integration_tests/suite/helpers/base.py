# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import os

from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from wazo_admin_ui_test_helpers.asset_launching_test_case import AdminUIAssetLaunchingTestCase
from wazo_admin_ui_test_helpers.pages.browser import Browser
from wazo_admin_ui_test_helpers.pages.page import Page
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
        username = 'xivo-auth-mock-doesnt-care-about-username'
        password = 'xivo-auth-mock-doesnt-care-about-password'
        Page.CONFIG['base_url'] = 'https://admin-ui:9296'

        browser_port = cls.service_port(4444, 'browser')
        remote_url = 'http://localhost:{port}/wd/hub'.format(port=browser_port)
        browser = RemoteBrowser(remote_url, username, password)

        browser.pages['users'] = UserListPage
        return browser


class RemoteBrowser(Browser):

    def __init__(self, remote_url, username, password):
        self.remote_url = remote_url
        self.username = username
        self.password = password

    def start(self):
        self.driver = webdriver.Remote(command_executor=self.remote_url, desired_capabilities=DesiredCapabilities.FIREFOX)
        self.driver.set_window_size(1920, 1080)
        self._login()

    def stop(self):
        self.driver.close()
