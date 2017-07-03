# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from hamcrest import assert_that, equal_to, contains_inanyorder, has_item

from xivo_test_helpers.confd import fixtures
from xivo_test_helpers.confd import associations as a
from xivo_test_helpers.confd import scenarios as s
from .test_api.base import IntegrationTest


class TestUser(IntegrationTest):

    asset = 'base'

    def test_create_without_extension(self):
        page = self.browser.users
        page.display_add_form()
        page.fill_name('firstname', 'firstname1')
        page.fill_name('lastname', 'lastname1')
        page.save()

        page = self.browser.users
        row = page.get_row('firstname1')
        assert_that(row.extract('Firstname'), equal_to('firstname1'))
        assert_that(row.extract('Lastname'), equal_to('lastname1'))
        assert_that(row.extract('Extension'), equal_to('-'))
        assert_that(row.extract('Code'), equal_to('-'))

    def test_create_with_email(self):
        email = 'email2@example.com'
        page = self.browser.users
        page.display_add_form()
        page.fill_name('firstname', 'firstname2')
        page.fill_name('email', email)
        page.fill_name('password', 'password2')
        page.save()

        page = self.browser.users
        user2 = page.edit('firstname2')
        assert_that(user2.get_value('firstname'), equal_to('firstname2'))
        assert_that(user2.get_value('email'), equal_to(email))
        assert_that(user2.get_value('username'), equal_to(email))
        assert_that(user2.get_value('password'), equal_to('password2'))

    @fixtures.user()
    @fixtures.line_sip()
    @fixtures.line_sip()
    def test_edit_with_multi_lines(self, user, line1, line2):
        with a.user_line(user, line1), a.user_line(user, line2):
            page = self.browser.users.edit_by_id(user['uuid'])
            page.save()

    @fixtures.user(firstname='Bob',
                   lastname='ette',
                   email='bob.ette@example.com',
                   username='bette',
                   password='password',
                   mobile_phone_number='5555555555',
                   ring_seconds=12,
                   music_on_hold='default',
                   simultaneous_calls=20,
                   timezone='na-eastern',
                   preprocess_subroutine='my_subroutine',
                   userfield='montreal,quebec,sageunay',
                   description='Amazing description',
                   services={'dnd': {'enabled': True},
                             'incallfilter': {'enabled': False}},
                   forwards={'busy': {'enabled': True,
                                      'destination': '123'},
                             'unconditional': {'enabled': False,
                                               'destination': '456'},
                             'noanswer': {'enabled': False,
                                          'destination': None}},
                   fallbacks={'busy_destination': {'type': 'none'},
                              'congestion_destination': None,
                              'fail_destination': {'type': 'hangup',
                                                   'cause': 'busy'},
                              'noanswer_destination': {'type': 'application',
                                                       'application': 'disa',
                                                       'context': 'default',
                                                       'pin': '123'}})
    def test_edit_with_same_user_params(self, user):
        page = self.browser.users.edit_by_id(user['uuid'])

        assert_that(page.get_value('firstname'), equal_to(user['firstname']))
        assert_that(page.get_value('lastname'), equal_to(user['lastname']))
        assert_that(page.get_value('email'), equal_to(user['email']))
        assert_that(page.get_value('username'), equal_to(user['username']))
        assert_that(page.get_value('password'), equal_to(user['password']))
        assert_that(page.get_value('mobile_phone_number'), equal_to(user['mobile_phone_number']))
        assert_that(page.get_value('ring_seconds'), unicode(equal_to(user['ring_seconds'])))
        assert_that(page.get_value('music_on_hold'), equal_to(user['music_on_hold']))
        assert_that(page.get_value('simultaneous_calls'), unicode(equal_to(user['simultaneous_calls'])))
        assert_that(page.get_value('timezone'), equal_to(user['timezone']))
        assert_that(page.get_value('preprocess_subroutine'), equal_to(user['preprocess_subroutine']))
        assert_that(page.get_value('userfield'), equal_to(user['userfield']))
        assert_that(page.get_value('description'), equal_to(user['description']))

        assert_that(page.get_checked('services-dnd-enabled'),
                    equal_to(user['services']['dnd']['enabled']))
        assert_that(page.get_checked('services-incallfilter-enabled'),
                    equal_to(user['services']['incallfilter']['enabled']))

        assert_that(page.get_checked('forwards-busy-enabled'),
                    equal_to(user['forwards']['busy']['enabled']))
        assert_that(page.get_value('forwards-busy-destination'),
                    equal_to(user['forwards']['busy']['destination']))
        assert_that(page.get_checked('forwards-unconditional-enabled'),
                    equal_to(user['forwards']['unconditional']['enabled']))
        assert_that(page.get_value('forwards-unconditional-destination'),
                    equal_to(user['forwards']['unconditional']['destination']))
        assert_that(page.get_checked('forwards-noanswer-enabled'),
                    equal_to(user['forwards']['noanswer']['enabled']))
        assert_that(page.get_value('forwards-noanswer-destination'),
                    equal_to(''))

        assert_that(page.get_selected_option_value('fallbacks-busy_destination-type'),
                    equal_to(user['fallbacks']['busy_destination']['type']))

        assert_that(page.get_selected_option_value('fallbacks-congestion_destination-type'),
                    equal_to('none'))

        assert_that(page.get_selected_option_value('fallbacks-fail_destination-type'),
                    equal_to(user['fallbacks']['fail_destination']['type']))
        assert_that(page.get_selected_option_value('fallbacks-fail_destination-hangup-cause'),
                    equal_to(user['fallbacks']['fail_destination']['cause']))

        assert_that(page.get_selected_option_value('fallbacks-noanswer_destination-type'),
                    equal_to(user['fallbacks']['noanswer_destination']['type']))
        assert_that(page.get_selected_option_value('fallbacks-noanswer_destination-application-application'),
                    equal_to(user['fallbacks']['noanswer_destination']['application']))
        assert_that(page.get_value('fallbacks-noanswer_destination-application-disa-context'),
                    equal_to(user['fallbacks']['noanswer_destination']['context']))
        assert_that(page.get_value('fallbacks-noanswer_destination-application-disa-pin'),
                    equal_to(user['fallbacks']['noanswer_destination']['pin']))
        page.save()

    @fixtures.user()
    def test_installed_destination_type(self, user):
        page = self.browser.users.edit_by_id(user['uuid'])
        fallbacks_tab = page.fallbacks()
        for fallback in ('noanswer_destination',
                         'busy_destination',
                         'congestion_destination',
                         'fail_destination'):
            dest = getattr(fallbacks_tab, fallback)()
            assert_that(dest.type_choices(), contains_inanyorder(
                'None',
                'Custom',
                'Sound',
                'Hangup',
                'Application',
                'User',
            ))

    @fixtures.user()
    def test_hangup_destination(self, user):
        page = self.browser.users.edit_by_id(user['uuid'])
        fallbacks_tab = page.fallbacks()

        for fallback in ('noanswer_destination',
                         'busy_destination',
                         'congestion_destination',
                         'fail_destination'):
            dest = getattr(fallbacks_tab, fallback)()
            assert_that(dest.type_choices(), has_item('Hangup'))

            dest.select_type('Hangup')
            assert_that(dest.get_selected_type_value(), equal_to('hangup'))
            assert_that(page.is_savable())

            dest.select_redirection('Normal')
            assert_that(dest.get_selected_redirection_value(), equal_to('normal'))
            assert_that(page.is_savable())

            dest.select_redirection('Busy')
            assert_that(dest.get_selected_redirection_value(), equal_to('busy'))
            assert_that(page.is_savable())

            dest.fill_sub_redirection_option('timeout', -1)
            assert_that(page.is_not_savable())
            dest.fill_sub_redirection_option('timeout', 30)
            assert_that(dest.get_sub_redirection_option_value('timeout'), equal_to('30'))
            assert_that(page.is_savable())

            dest.select_redirection('Congestion')
            assert_that(dest.get_selected_redirection_value(), equal_to('congestion'))
            assert_that(page.is_savable())

            dest.fill_sub_redirection_option('timeout', -1)
            assert_that(page.is_not_savable())
            dest.fill_sub_redirection_option('timeout', 30)
            assert_that(dest.get_sub_redirection_option_value('timeout'), equal_to('30'))
            assert_that(page.is_savable())

    @fixtures.user()
    def test_sound_destination(self, user):
        page = self.browser.users.edit_by_id(user['uuid'])
        fallbacks_tab = page.fallbacks()

        for fallback in ('noanswer_destination',
                         'busy_destination',
                         'congestion_destination',
                         'fail_destination'):
            dest = getattr(fallbacks_tab, fallback)()
            assert_that(dest.type_choices(), has_item('Sound'))

            dest.select_type('Sound')
            assert_that(dest.get_selected_type_value(), equal_to('sound'))
            assert_that(page.is_not_savable())

            dest.fill_redirection_option('filename', s.random_string(300))
            assert_that(len(dest.get_redirection_option_value('filename')), equal_to(255))
            dest.fill_redirection_option('filename', 'hello-world')
            assert_that(dest.get_redirection_option_value('filename'), 'hello-world')
            assert_that(page.is_savable())

            dest.fill_redirection_option('skip', True)
            assert_that(dest.get_redirection_option_value('skip'), equal_to(True))
            assert_that(page.is_savable())

            dest.fill_redirection_option('no_answer', True)
            assert_that(dest.get_redirection_option_value('no_answer'), equal_to(True))
            assert_that(page.is_savable())

    @fixtures.user()
    def test_custom_destination(self, user):
        page = self.browser.users.edit_by_id(user['uuid'])
        fallbacks_tab = page.fallbacks()

        for fallback in ('noanswer_destination',
                         'busy_destination',
                         'congestion_destination',
                         'fail_destination'):
            dest = getattr(fallbacks_tab, fallback)()
            assert_that(dest.type_choices(), has_item('Custom'))

            dest.select_type('Custom')
            assert_that(dest.get_selected_type_value(), equal_to('custom'))
            assert_that(page.is_not_savable())

            dest.fill_redirection_option('command', s.random_string(300))
            assert_that(len(dest.get_redirection_option_value('command')), equal_to(255))
            dest.fill_redirection_option('command', 'rm -rf /')
            assert_that(dest.get_redirection_option_value('command'), 'rm -rf /')
            assert_that(page.is_savable())

    @fixtures.user()
    def test_none_destination(self, user):
        page = self.browser.users.edit_by_id(user['uuid'])
        fallbacks_tab = page.fallbacks()

        for fallback in ('noanswer_destination',
                         'busy_destination',
                         'congestion_destination',
                         'fail_destination'):
            dest = getattr(fallbacks_tab, fallback)()
            assert_that(dest.type_choices(), has_item('None'))

            dest.select_type('None')
            assert_that(dest.get_selected_type_value(), equal_to('none'))
            assert_that(page.is_savable())

    @fixtures.user()
    def test_application_destination(self, user):
        page = self.browser.users.edit_by_id(user['uuid'])
        fallbacks_tab = page.fallbacks()

        for fallback in ('noanswer_destination',
                         'busy_destination',
                         'congestion_destination',
                         'fail_destination'):
            dest = getattr(fallbacks_tab, fallback)()
            assert_that(dest.type_choices(), has_item('Application'))

            dest.select_type('Application')
            assert_that(dest.get_selected_type_value(), equal_to('application'))
            assert_that(page.is_not_savable())

            dest.select_redirection('CallBack DISA')
            assert_that(dest.get_selected_redirection_value(), equal_to('callback_disa'))
            assert_that(page.is_not_savable())

            dest.fill_sub_redirection_option('context', s.random_string(42))
            assert_that(len(dest.get_sub_redirection_option_value('context')), equal_to(39))
            dest.fill_sub_redirection_option('context', '!invalid?')
            assert_that(page.is_not_savable())
            dest.fill_sub_redirection_option('context', 'Valid-123_')
            assert_that(dest.get_sub_redirection_option_value('context'), equal_to('Valid-123_'))
            assert_that(page.is_savable())

            dest.fill_sub_redirection_option('pin', s.random_string(42))
            assert_that(len(dest.get_sub_redirection_option_value('pin')), equal_to(40))
            assert_that(page.is_not_savable())
            dest.fill_sub_redirection_option('pin', 'invalid')
            assert_that(page.is_not_savable())
            dest.fill_sub_redirection_option('pin', '1234')
            assert_that(dest.get_sub_redirection_option_value('pin'), equal_to('1234'))
            assert_that(page.is_savable())

            dest.select_redirection('Directory')
            assert_that(dest.get_selected_redirection_value(), equal_to('directory'))
            assert_that(page.is_not_savable())

            dest.fill_sub_redirection_option('context', s.random_string(42))
            assert_that(len(dest.get_sub_redirection_option_value('context')), equal_to(39))
            dest.fill_sub_redirection_option('context', '!invalid?')
            assert_that(page.is_not_savable())
            dest.fill_sub_redirection_option('context', 'Valid-123_')
            assert_that(dest.get_sub_redirection_option_value('context'), equal_to('Valid-123_'))
            assert_that(page.is_savable())

            dest.select_redirection('DISA')
            assert_that(dest.get_selected_redirection_value(), equal_to('disa'))
            assert_that(page.is_not_savable())

            dest.fill_sub_redirection_option('context', s.random_string(42))
            assert_that(len(dest.get_sub_redirection_option_value('context')), equal_to(39))
            dest.fill_sub_redirection_option('context', '!invalid?')
            assert_that(page.is_not_savable())
            dest.fill_sub_redirection_option('context', 'Valid-123_')
            assert_that(dest.get_sub_redirection_option_value('context'), equal_to('Valid-123_'))
            assert_that(page.is_savable())

            dest.fill_sub_redirection_option('pin', s.random_string(42))
            assert_that(len(dest.get_sub_redirection_option_value('pin')), equal_to(40))
            dest.fill_sub_redirection_option('pin', 'invalid')
            assert_that(page.is_not_savable())
            dest.fill_sub_redirection_option('pin', '1234')
            assert_that(dest.get_sub_redirection_option_value('pin'), equal_to('1234'))
            assert_that(page.is_savable())

            dest.select_redirection('Fax To Mail')
            assert_that(dest.get_selected_redirection_value(), equal_to('fax_to_mail'))
            assert_that(page.is_not_savable())

            dest.fill_sub_redirection_option('email', s.random_string(82))
            assert_that(len(dest.get_sub_redirection_option_value('email')), equal_to(80))
            dest.fill_sub_redirection_option('email', 'invalid_email')
            assert_that(page.is_not_savable())
            dest.fill_sub_redirection_option('email', 'bob.ino@example.com')
            assert_that(dest.get_sub_redirection_option_value('email'), equal_to('bob.ino@example.com'))
            assert_that(page.is_savable())

            dest.select_redirection('Voicemail')
            assert_that(dest.get_selected_redirection_value(), equal_to('voicemail'))
            assert_that(page.is_not_savable())

            dest.fill_sub_redirection_option('context', s.random_string(42))
            assert_that(len(dest.get_sub_redirection_option_value('context')), equal_to(39))
            dest.fill_sub_redirection_option('context', '!invalid?')
            assert_that(page.is_not_savable())
            dest.fill_sub_redirection_option('context', 'Valid-123_')
            assert_that(dest.get_sub_redirection_option_value('context'), equal_to('Valid-123_'))
            assert_that(page.is_savable())

    @fixtures.user(firstname='Bob', lastname='Ino')
    def test_user_destination(self, user):
        page = self.browser.users.edit_by_id(user['uuid'])
        fallbacks_tab = page.fallbacks()

        for fallback in ('noanswer_destination',
                         'busy_destination',
                         'congestion_destination',
                         'fail_destination'):
            dest = getattr(fallbacks_tab, fallback)()
            assert_that(dest.type_choices(), has_item('User'))

            dest.select_type('User')
            assert_that(dest.get_selected_type_value(), equal_to('user'))
            assert_that(page.is_not_savable())

            dest.select_redirection('Bob Ino')
            assert_that(dest.get_selected_redirection_value(), equal_to(unicode(user['id'])))
            assert_that(page.is_savable())

            fallback_destination.fill_redirection_option('ring_time', '-1')
            assert_that(page.is_not_savable())
            fallback_destination.fill_redirection_option('ring_time', '30')
            assert_that(fallback_destination.get_redirection_option_value('ring_time'), equal_to('30'))
            assert_that(page.is_savable())
