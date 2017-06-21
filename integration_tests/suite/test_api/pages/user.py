# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_test_helpers.admin_ui.pages.page import Page, ListPage


class UserPage(Page):
    pass


class UserListPage(ListPage):

    url = "/users"
    form_page = UserPage
