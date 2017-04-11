# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import unittest

from mock import Mock, call

import wazo_admin_ui.helpers.service
import user.service
from ..service import UserService


class TestUserService(unittest.TestCase):

    def setUp(self):
        self._confd_users = Mock()
        self._confd_lines = Mock()
        self._confd_extensions = Mock()
        self._confd_endpoints_sip = Mock()
        self._confd_endpoints_sccp = Mock()
        self._confd_endpoints_custom = Mock()
        confd = Mock(users=self._confd_users,
                     lines=self._confd_lines,
                     extensions=self._confd_extensions,
                     endpoints_sip=self._confd_endpoints_sip,
                     endpoints_sccp=self._confd_endpoints_sccp,
                     endpoints_custom=self._confd_endpoints_custom)
        user.service.confd = confd
        wazo_admin_ui.helpers.service.confd = confd
        self.service = UserService()

    def test_update_with_no_lines(self):
        resource = {'uuid': '1234', 'lines': []}
        self._confd_users.get.return_value = {'lines': []}

        self.service.update(resource)

        self._confd_lines.update.assert_not_called()
        self._confd_lines.create.assert_not_called()
        self._confd_lines.delete.assert_not_called()

    def test_update_with_lines_when_no_existing_lines(self):
        resource = {'uuid': '1234', 'lines': [{'id': ''}]}
        self._confd_users.get.return_value = {'lines': []}
        self._confd_lines.create.return_value = {'id': 'new-line-id'}

        self.service.update(resource)

        self._confd_users.return_value.add_line.assert_called_once_with({'id': 'new-line-id'})
        self._confd_lines.create.assert_called_once_with({'id': 'new-line-id'})
        self._confd_lines.update.assert_not_called()
        self._confd_lines.delete.assert_not_called()

    def test_update_with_lines_when_existing_lines_with_same_id(self):
        resource = {'uuid': '1234', 'lines': [{'id': 'line-id'}]}
        self._confd_users.get.return_value = {'lines': [{'id': 'line-id'}]}
        self._confd_lines.get.return_value = {'extensions': []}

        self.service.update(resource)

        self._confd_lines.update.assert_called_once_with({'id': 'line-id'})
        self._confd_lines.create.assert_not_called()
        self._confd_lines.delete.assert_not_called()

    def test_update_with_lines_when_existing_lines_with_same_id_and_same_extension(self):
        line = {'id': 'line-id', 'extensions': [{'id': 'extension-id', 'exten': '999'}]}
        resource = {'uuid': '1234', 'lines': [line]}
        self._confd_users.get.return_value = {'lines': [{'id': 'line-id'}]}
        self._confd_lines.get.return_value = {'extensions': [{'id': 'extension-id'}]}

        self.service.update(resource)

        self._confd_lines.update.assert_called_once_with(line)
        self._confd_extensions.update.assert_called_once_with({'id': 'extension-id', 'exten': '999'})
        self._confd_lines.create.assert_not_called()
        self._confd_lines.delete.assert_not_called()

    def test_update_with_lines_when_existing_lines_with_same_id_and_no_existing_extension(self):
        extension1 = {'id': '', 'exten': '12', 'context': 'default'}
        line = {'id': 'line-id', 'extensions': [extension1]}
        resource = {'uuid': '1234', 'lines': [line]}
        self._confd_users.get.return_value = {'lines': [{'id': 'line-id'}]}
        self._confd_lines.get.return_value = {'extensions': []}
        self._confd_extensions.create.return_value = {'id': 'extension-id'}
        self._confd_extensions.list.return_value = {'items': []}

        self.service.update(resource)

        self._confd_lines.update.assert_called_once_with(line)
        self._confd_extensions.create.assert_called_once_with(extension1)
        self._confd_lines.return_value.add_extension.assert_called_once_with({'id': 'extension-id'})
        self._confd_lines.create.assert_not_called()
        self._confd_lines.delete.assert_not_called()

    def test_update_with_lines_when_existing_lines_with_same_id_and_existing_extension_not_on_existing_line(self):
        extension1 = {'id': '', 'exten': '12', 'context': 'default'}
        line = {'id': 'line-id', 'extensions': [extension1]}
        resource = {'uuid': '1234', 'lines': [line]}
        self._confd_users.get.return_value = {'lines': [{'id': 'line-id'}]}
        self._confd_lines.get.return_value = {'extensions': []}
        self._confd_extensions.list.return_value = {'items': [extension1]}

        self.service.update(resource)

        self._confd_lines.update.assert_called_once_with(line)
        self._confd_extensions.create.assert_not_called()
        self._confd_lines.return_value.add_extension.assert_called_once_with(extension1)
        self._confd_lines.create.assert_not_called()
        self._confd_lines.delete.assert_not_called()

    def test_update_with_lines_when_existing_lines_with_same_id_and_no_extension(self):
        line = {'id': 'line-id', 'extensions': []}
        resource = {'uuid': '1234', 'lines': [line]}
        self._confd_users.get.return_value = {'lines': [{'id': 'line-id'}]}
        self._confd_lines.get.return_value = {'extensions': [{'id': 'extension-id'}]}
        self._confd_extensions.create.return_value = {'id': 'extension-id'}

        self.service.update(resource)

        self._confd_lines.update.assert_called_once_with(line)
        self._confd_extensions.delete.assert_called_once_with({'id': 'extension-id'})
        self._confd_lines.return_value.remove_extension.assert_called_once_with({'id': 'extension-id'})
        self._confd_lines.create.assert_not_called()
        self._confd_lines.delete.assert_not_called()

    def test_update_with_lines_when_existing_lines_with_same_id_and_endpoint_sip(self):
        line = {'id': 'line-id', 'endpoint_sip': {'id': 'endpoint-sip-id'}}
        resource = {'uuid': '1234', 'lines': [line]}
        self._confd_users.get.return_value = {'lines': [{'id': 'line-id'}]}
        self._confd_lines.get.return_value = {'extensions': []}

        self.service.update(resource)

        self._confd_lines.update.assert_called_once_with(line)
        self._confd_endpoints_sip.update.assert_called_once_with({'id': 'endpoint-sip-id'})
        self._confd_lines.create.assert_not_called()
        self._confd_lines.delete.assert_not_called()

    def test_update_with_lines_with_id_when_not_existing_lines(self):
        line = {'id': 'line-id'}
        resource = {'uuid': '1234', 'lines': [line]}
        self._confd_users.get.return_value = {'lines': []}
        self._confd_lines.get.return_value = {'extensions': []}

        self.service.update(resource)

        self._confd_lines.update.assert_called_once_with(line)
        self._confd_users.return_value.add_line.assert_called_once_with(line)

    def test_update_with_lines_with_endpoint_sip_when_no_existing_lines(self):
        resource = {'uuid': '1234', 'lines': [{'endpoint_sip': {}}]}
        self._confd_users.get.return_value = {'lines': []}
        self._confd_lines.get.return_value = {'extensions': []}
        self._confd_lines.create.return_value = {'id': 'new-line-id'}
        self._confd_endpoints_sip.create.return_value = {'id': 'new-sip-id'}

        self.service.update(resource)

        self._confd_endpoints_sip.create.assert_called_once_with({})
        self._confd_lines.return_value.add_endpoint_sip.assert_called_once_with({'id': 'new-sip-id'})

    def test_update_with_lines_with_endpoint_sccp_when_no_existing_lines(self):
        resource = {'uuid': '1234', 'lines': [{'endpoint_sccp': {}}]}
        self._confd_users.get.return_value = {'lines': []}
        self._confd_lines.get.return_value = {'extensions': []}
        self._confd_lines.create.return_value = {'id': 'new-line-id'}
        self._confd_endpoints_sccp.create.return_value = {'id': 'new-sccp-id'}

        self.service.update(resource)

        self._confd_endpoints_sccp.create.assert_called_once_with({})
        self._confd_lines.return_value.add_endpoint_sccp.assert_called_once_with({'id': 'new-sccp-id'})

    def test_update_with_lines_with_endpoint_custom_when_no_existing_lines(self):
        resource = {'uuid': '1234', 'lines': [{'endpoint_custom': {}}]}
        self._confd_users.get.return_value = {'lines': []}
        self._confd_lines.get.return_value = {'extensions': []}
        self._confd_lines.create.return_value = {'id': 'new-line-id'}
        self._confd_endpoints_custom.create.return_value = {'id': 'new-custom-id'}

        self.service.update(resource)

        self._confd_endpoints_custom.create.assert_called_once_with({})
        self._confd_lines.return_value.add_endpoint_custom.assert_called_once_with({'id': 'new-custom-id'})

    def test_update_with_no_lines_when_existing_lines(self):
        resource = {'uuid': '1234', 'lines': []}
        self._confd_users.get.return_value = {'lines': [{'id': 'line-id'}]}
        self._confd_lines.get.return_value = confd_line = {'extensions': []}

        self.service.update(resource)

        self._confd_users.return_value.remove_line.assert_called_once_with('line-id')
        self._confd_lines.delete.assert_called_once_with(confd_line)

    def test_update_with_no_lines_when_existing_lines_with_endpoint_sip(self):
        resource = {'uuid': '1234', 'lines': []}
        self._confd_users.get.return_value = {'lines': [{'id': 'line-id'}]}
        self._confd_lines.get.return_value = confd_line = {'extensions': [], 'endpoint_sip': {'id': 'sip-id'}}

        self.service.update(resource)

        self._confd_lines.return_value.remove_endpoint_sip.assert_called_once_with({'id': 'sip-id'})
        self._confd_endpoints_sip.delete.assert_called_once_with({'id': 'sip-id'})
        self._confd_users.return_value.remove_line.assert_called_once_with('line-id')
        self._confd_lines.delete.assert_called_once_with(confd_line)

    def test_update_with_no_lines_when_existing_lines_with_endpoint_sccp(self):
        resource = {'uuid': '1234', 'lines': []}
        self._confd_users.get.return_value = {'lines': [{'id': 'line-id'}]}
        self._confd_lines.get.return_value = confd_line = {'extensions': [], 'endpoint_sccp': {'id': 'sccp-id'}}

        self.service.update(resource)

        self._confd_lines.return_value.remove_endpoint_sccp.assert_called_once_with({'id': 'sccp-id'})
        self._confd_endpoints_sccp.delete.assert_called_once_with({'id': 'sccp-id'})
        self._confd_users.return_value.remove_line.assert_called_once_with('line-id')
        self._confd_lines.delete.assert_called_once_with(confd_line)

    def test_update_with_no_lines_when_existing_lines_with_endpoint_custom(self):
        resource = {'uuid': '1234', 'lines': []}
        self._confd_users.get.return_value = {'lines': [{'id': 'line-id'}]}
        self._confd_lines.get.return_value = confd_line = {'extensions': [], 'endpoint_custom': {'id': 'custom-id'}}

        self.service.update(resource)

        self._confd_lines.return_value.remove_endpoint_custom.assert_called_once_with({'id': 'custom-id'})
        self._confd_endpoints_custom.delete.assert_called_once_with({'id': 'custom-id'})
        self._confd_users.return_value.remove_line.assert_called_once_with('line-id')
        self._confd_lines.delete.assert_called_once_with(confd_line)

    def test_update_with_no_lines_when_existing_lines_with_extensions(self):
        resource = {'uuid': '1234', 'lines': []}
        self._confd_users.get.return_value = {'lines': [{'id': 'line-id'}]}
        self._confd_lines.get.return_value = confd_line = {'extensions': [{'id': 'extension-id'}]}

        self.service.update(resource)

        self._confd_lines.return_value.remove_extension.assert_called_once_with({'id': 'extension-id'})
        self._confd_extensions.delete.assert_called_once_with({'id': 'extension-id'})
        self._confd_users.return_value.remove_line.assert_called_once_with('line-id')
        self._confd_lines.delete.assert_called_once_with(confd_line)

    def test_update_when_swapping_lines(self):
        line1 = {'id': 'line1-id'}
        line2 = {'id': 'line2-id'}
        resource = {'uuid': '1234', 'lines': [line2, line1]}
        self._confd_users.get.return_value = {'lines': [line1, line2]}
        self._confd_lines.get.return_value = {'extensions': []}

        self.service.update(resource)

        self._confd_users.return_value.remove_line.assert_has_calls(
            [call('line1-id'), call('line2-id')], any_order=True
        )
        self._confd_lines.update.assert_has_calls([call(line2), call(line1)])
        self._confd_users.return_value.add_line.assert_has_calls([call(line2), call(line1)])
        self._confd_lines.delete.assert_not_called()
