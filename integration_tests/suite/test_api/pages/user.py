# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from xivo_test_helpers.admin_ui.pages.page import Page, ListPage
from xivo_test_helpers.admin_ui.pages.select2 import Select2


class UserPage(Page):

    def fallbacks(self):
        self._select_tab('fallbacks')
        return FallbacksTab(self.driver)

    def services(self):
        self._select_tab('services')
        return ServicesTab(self.driver)

    def general(self):
        self._select_tab('general')
        return Page(self.driver)

    def user(self):
        self._select_tab('user')
        return Page(self.driver)

    def _select_tab(self, id_):
        link = self.driver.find_element_by_css_selector("a[href='#{}']".format(id_))
        link.click()
        self.wait_visible(By.ID, id_)


class FallbacksTab(Page):

    def noanswer_destination(self):
        return DestinationSection(self.driver, 'fallbacks-noanswer_destination')

    def busy_destination(self):
        return DestinationSection(self.driver, 'fallbacks-busy_destination')

    def congestion_destination(self):
        return DestinationSection(self.driver, 'fallbacks-congestion_destination')

    def fail_destination(self):
        return DestinationSection(self.driver, 'fallbacks-fail_destination')


class ServicesTab(Page):

    def busy(self):
        return ForwardSection(self.driver, 'busy')

    def noanswer(self):
        return ForwardSection(self.driver, 'noanswer')

    def unconditional(self):
        return ForwardSection(self.driver, 'unconditional')


class ForwardSection(Page):

    def __init__(self, driver, section):
        super(ForwardSection, self).__init__(driver)
        self.section = section

    @property
    def section_id(self):
        return 'forwards-{}'.format(self.section)

    @property
    def enabled_id(self):
        return '{}-enabled'.format(self.section_id)

    @property
    def destination_id(self):
        return '{}-destination'.format(self.section_id)

    def enable(self):
        self.fill_id(self.enabled_id, True)

    def disable(self):
        self.fill_id(self.enabled_id, False)

    def fill_destination(self, value):
        self.fill_id(self.destination_id, value)

    def get_destination(self):
        return self.get_value(self.destination_id)


class DestinationSection(Page):

    def __init__(self, driver, section):
        super(DestinationSection, self).__init__(driver)
        self.section = section
        self.destination = None

    @property
    def type_id(self):
        return '{}-type'.format(self.section)

    def select_type(self, destination):
        self.destination = destination
        self.select_id(self.type_id, destination)
        self.get_destination_not_hidden()

    def get_selected_type_value(self):
        return self.get_selected_option_value(self.type_id)

    def type_choices(self):
        items = self.select2(By.ID, self.type_id).items
        return [item.text for item in items]

    def get_destination_not_hidden(self):
        destination = self.get_selected_option_value(self.type_id)
        xpath = '//div[.//select[@id="{}"]]/div[@class="destination-{}"]'.format(self.type_id, destination)
        self.wait_for(By.XPATH, xpath)
        return self.driver.find_element_by_xpath(xpath)

    def get_destinations_hidden(self):
        destination = self.get_selected_option_value(self.type_id)
        xpath = '//div[.//select[@id="{}"]]/div[@class="destination-{} hidden"]'.format(self.type_id, destination)
        return self.driver.find_element_by_xpath(xpath)

    def select_redirection(self, value):
        redirection_section = self.get_destination_not_hidden()
        redirection_select = redirection_section.find_element_by_css_selector('select')
        Select2(redirection_select, self.driver).select(value)

    def get_selected_redirection_value(self):
        redirection_section = self.get_destination_not_hidden()
        redirection_select = redirection_section.find_element_by_css_selector('select')
        redirection_select_id = redirection_select.get_attribute('id')
        return self.get_selected_option_value(redirection_select_id)

    def redirection_list(self):
        selector = '[id^={}-{}] select'.format(self.section, self.destination)
        try:
            dropdown = Select(self.driver.find_element_by_css_selector(selector))
        except NoSuchElementException:
            return None
        return [o.text for o in dropdown.options]

    def fill_redirection_option(self, option, value):
        option_id = '{}-{}-{}'.format(self.section, self.get_selected_type_value(), option)
        self.fill_id(option_id, value)

    def get_redirection_option_value(self, option):
        option_id = '{}-{}-{}'.format(self.section, self.get_selected_type_value(), option)
        el = self.driver.find_element_by_id(option_id)
        if el.get_attribute('type') == 'checkbox':
            return self.get_checked(option_id)
        return self.get_value(option_id)

    def fill_sub_redirection_option(self, option, value):
        option_id = '{}-{}-{}-{}'.format(self.section,
                                         self.get_selected_type_value(),
                                         self.get_selected_redirection_value(),
                                         option)
        self.fill_id(option_id, value)

    def get_sub_redirection_option_value(self, option):
        option_id = '{}-{}-{}-{}'.format(self.section,
                                         self.get_selected_type_value(),
                                         self.get_selected_redirection_value(),
                                         option)
        return self.get_value(option_id)


class UserListPage(ListPage):

    url = "/users"
    form_page = UserPage
