# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import unittest

from mock import Mock, call

import wazo_admin_ui.helpers.service
import wazo_plugind_admin_ui_user_official.service as service
from ..service import UserService


class TestUserServiceUpdateUserLines(unittest.TestCase):

    def setUp(self):
        self.confd = Mock()
        service.confd = self.confd
        wazo_admin_ui.helpers.service.confd = self.confd
        self.service = UserService()
        self.confd.lines.get.return_value = {'extensions': [], 'device_id': None}

    def test_when_line_and_existing_line_with_same_id(self):
        line = {'id': 'line-id'}
        user = {'uuid': '1234', 'lines': [line]}
        self.confd.users.get.return_value = {'lines': [line]}

        self.service._update_user_lines(user)

        self._assert_line_updated(line)

    def test_when_line_and_existing_line_with_same_id_and_same_extension(self):
        extension = {'id': 'extension-id', 'exten': '999', 'context': 'default'}
        line = {'id': 'line-id', 'extensions': [extension]}
        user = {'uuid': '1234', 'lines': [line]}
        self.confd.users.get.return_value = {'lines': [{'id': 'line-id'}]}
        self.confd.extensions.get.return_value = {'lines': [{}], 'exten': '999', 'context': 'default'}
        self.confd.lines.get.return_value = {'device_id': None, 'extensions': [{'id': 'extension-id'}]}

        self.service._update_user_lines(user)

        self._assert_line_updated(line)
        self.confd.extensions.update.assert_not_called()

    def test_when_line_and_existing_line_with_same_id_and_existing_extension_not_on_existing_line(self):
        extension1 = {'id': '', 'exten': '12', 'context': 'default'}
        line = {'id': 'line-id', 'extensions': [extension1]}
        user = {'uuid': '1234', 'lines': [line]}
        self.confd.users.get.return_value = {'lines': [{'id': 'line-id'}]}
        self.confd.lines.get.return_value = {'device_id': None, 'extensions': []}
        self.confd.extensions.list.return_value = {'items': [extension1]}

        self.service._update_user_lines(user)

        self._assert_line_updated(line)
        self.confd.extensions.create.assert_not_called()
        self.confd.lines.return_value.add_extension.assert_called_once_with(extension1)

    def test_when_line_and_existing_line_with_same_id_and_extension_and_no_existing_extension(self):
        extension1 = {'id': '', 'exten': '12', 'context': 'default'}
        line = {'id': 'line-id', 'extensions': [extension1]}
        user = {'uuid': '1234', 'lines': [line]}
        self.confd.users.get.return_value = {'lines': [{'id': 'line-id'}]}
        self.confd.lines.get.return_value = {'device_id': None, 'extensions': []}
        self.confd.extensions.create.return_value = {'id': 'extension-id'}
        self.confd.extensions.list.return_value = {'items': []}

        self.service._update_user_lines(user)

        self._assert_line_updated(line)
        self.confd.extensions.create.assert_called_once_with(extension1)
        self.confd.lines.return_value.add_extension.assert_called_once_with({'id': 'extension-id'})

    def test_when_line_and_existing_line_with_same_id_and_no_extension_and_existing_extension(self):
        line = {'id': 'line-id', 'extensions': []}
        user = {'uuid': '1234', 'lines': [line]}
        self.confd.users.get.return_value = {'lines': [{'id': 'line-id'}]}
        self.confd.lines.get.return_value = {'device_id': None, 'extensions': [{'id': 'extension-id'}]}
        self.confd.extensions.create.return_value = {'id': 'extension-id'}

        self.service._update_user_lines(user)

        self._assert_line_updated(line)
        self.confd.extensions.delete.assert_called_once_with({'id': 'extension-id'})
        self.confd.lines.return_value.remove_extension.assert_called_once_with({'id': 'extension-id'})

    def test_when_line_and_existing_line_with_same_id_and_endpoint_sip(self):
        line = {'id': 'line-id', 'endpoint_sip': {'id': 'endpoint-sip-id'}}
        user = {'uuid': '1234', 'lines': [line]}
        self.confd.users.get.return_value = {'lines': [{'id': 'line-id'}]}

        self.service._update_user_lines(user)

        self._assert_line_updated(line)
        self.confd.endpoints_sip.update.assert_called_once_with({'id': 'endpoint-sip-id'})

    def _assert_line_updated(self, line):
        self.confd.lines.update.assert_called_once_with(line)
        self.confd.lines.create.assert_not_called()
        self.confd.lines.delete.assert_not_called()

    def test_when_line_and_no_existing_line(self):
        user = {'uuid': '1234', 'lines': [{'id': ''}]}
        self.confd.users.get.return_value = {'lines': []}
        self.confd.lines.create.return_value = new_line = {'id': 'new-line-id'}

        self.service._update_user_lines(user)

        self.confd.lines.create.assert_called_once_with(new_line)
        self.confd.users.return_value.add_line.assert_called_once_with(new_line)
        self.confd.lines.update.assert_not_called()
        self.confd.lines.delete.assert_not_called()

    def test_when_line_and_no_existing_line_with_id(self):
        line = {'id': 'line-id'}
        user = {'uuid': '1234', 'lines': [line]}
        self.confd.users.get.return_value = {'lines': []}

        self.service._update_user_lines(user)

        self.confd.lines.update.assert_called_once_with(line)
        self.confd.users.return_value.add_line.assert_called_once_with(line)

    def test_when_line_and_no_existing_line_with_endpoint_sip(self):
        user = {'uuid': '1234', 'lines': [{'endpoint_sip': {}}]}
        self.confd.users.get.return_value = {'lines': []}
        self.confd.lines.create.return_value = {'id': 'new-line-id'}
        self.confd.endpoints_sip.create.return_value = {'id': 'new-sip-id'}

        self.service._update_user_lines(user)

        self.confd.endpoints_sip.create.assert_called_once_with({})
        self.confd.lines.return_value.add_endpoint_sip.assert_called_once_with({'id': 'new-sip-id'})

    def test_when_line_and_no_existing_line_with_endpoint_sccp(self):
        user = {'uuid': '1234', 'lines': [{'endpoint_sccp': {}}]}
        self.confd.users.get.return_value = {'lines': []}
        self.confd.lines.create.return_value = {'id': 'new-line-id'}
        self.confd.endpoints_sccp.create.return_value = {'id': 'new-sccp-id'}

        self.service._update_user_lines(user)

        self.confd.endpoints_sccp.create.assert_called_once_with({})
        self.confd.lines.return_value.add_endpoint_sccp.assert_called_once_with({'id': 'new-sccp-id'})

    def test_when_line_and_no_existing_line_with_endpoint_custom(self):
        user = {'uuid': '1234', 'lines': [{'endpoint_custom': {}}]}
        self.confd.users.get.return_value = {'lines': []}
        self.confd.lines.create.return_value = {'id': 'new-line-id'}
        self.confd.endpoints_custom.create.return_value = {'id': 'new-custom-id'}

        self.service._update_user_lines(user)

        self.confd.endpoints_custom.create.assert_called_once_with({})
        self.confd.lines.return_value.add_endpoint_custom.assert_called_once_with({'id': 'new-custom-id'})

    def test_when_line_and_no_existing_line_with_extension_and_no_existing_extension(self):
        extension = {'exten': '123', 'context': 'default'}
        user = {'uuid': '1234', 'lines': [{'endpoint_sip': {}, 'extensions': [extension]}]}
        self.confd.users.get.return_value = {'lines': []}
        self.confd.lines.create.return_value = {'id': 'new-line-id'}
        self.confd.extensions.create.return_value = {'id': 'new-extension-id'}
        self.confd.extensions.list.return_value = {'items': []}

        self.service._update_user_lines(user)

        self.confd.extensions.create.assert_called_once_with(extension)
        self.confd.lines.return_value.add_extension.assert_called_once_with({'id': 'new-extension-id'})

    def test_when_line_and_no_existing_line_with_extension_and_existing_extension(self):
        extension = {'exten': '123', 'context': 'default'}
        user = {'uuid': '1234', 'lines': [{'endpoint_sip': {}, 'extensions': [extension]}]}
        self.confd.users.get.return_value = {'lines': []}
        self.confd.lines.create.return_value = {'id': 'new-line-id'}
        self.confd.extensions.list.return_value = {'items': [{'id': 'extension-id'}]}

        self.service._update_user_lines(user)

        self.confd.extensions.create.assert_not_called()
        self.confd.lines.return_value.add_extension.assert_called_once_with({'id': 'extension-id'})

    def test_when_line_and_no_existing_line_with_device_id(self):
        user = {'uuid': '1234', 'lines': [{'endpoint_sip': {}, 'device_id': 'device-id'}]}
        self.confd.users.get.return_value = {'lines': []}
        self.confd.lines.create.return_value = {'id': 'new-line-id'}

        self.service._update_user_lines(user)

        self.confd.lines.return_value.add_device.assert_called_once_with('device-id')

    def test_when_no_line_and_no_existing_line(self):
        user = {'uuid': '1234', 'lines': []}
        self.confd.users.get.return_value = {'lines': []}

        self.service._update_user_lines(user)

        self.confd.lines.update.assert_not_called()
        self.confd.lines.create.assert_not_called()
        self.confd.lines.delete.assert_not_called()

    def test_when_no_line_and_existing_line(self):
        user = {'uuid': '1234', 'lines': []}
        self.confd.users.get.return_value = {'lines': [{'id': 'line-id'}]}
        self.confd.lines.get.return_value = {'device_id': 'device-id'}

        self.service._update_user_lines(user)

        self._assert_line_deleted('line-id')
        self.confd.lines.return_value.remove_device.assert_called_once_with('device-id')

    def _assert_line_deleted(self, line):
        self.confd.lines.delete.assert_called_once_with(line)
        self.confd.lines.create.assert_not_called()
        self.confd.lines.update.assert_not_called()

    def test_when_swapping_lines(self):
        line1 = {'id': 'line1-id'}
        line2 = {'id': 'line2-id'}
        user = {'uuid': '1234', 'lines': [line2, line1]}
        self.confd.users.get.return_value = {'lines': [line1, line2]}

        self.service._update_user_lines(user)

        self.confd.users.return_value.remove_line.assert_has_calls(
            [call('line1-id'), call('line2-id')], any_order=True
        )
        self.confd.lines.update.assert_has_calls([call(line2), call(line1)])
        self.confd.users.return_value.add_line.assert_has_calls([call(line2), call(line1)])
        self.confd.lines.delete.assert_not_called()

    def test_when_swapping_lines_with_device_then_device_is_dissociated(self):
        line1 = {'id': 'line1-id', 'device_id': 'device1-id'}
        line2 = {'id': 'line2-id', 'device_id': 'device2-id'}
        user = {'uuid': '1234', 'lines': [line2, line1]}
        self.confd.users.get.return_value = {'lines': [line1, line2]}
        self.confd.lines.get.side_effect = lambda x: {'line1-id': {'device_id': 'device1-id'},
                                                      'line2-id': {'device_id': 'device2-id'}}[x]

        self.service._update_user_lines(user)

        self.confd.lines.return_value.remove_device.assert_has_calls(
            [call('device1-id'), call('device2-id')], any_order=True
        )

    def test_when_swapping_lines_with_device_then_device_is_reassociated(self):
        line1 = {'id': 'line1-id', 'device_id': 'device1-id'}
        line2 = {'id': 'line2-id', 'device_id': 'device2-id'}
        user = {'uuid': '1234', 'lines': [line2, line1]}
        self.confd.users.get.return_value = {'lines': [line1, line2]}
        self.confd.lines.get.return_value = {'device_id': None}

        self.service._update_user_lines(user)

        self.confd.lines.return_value.add_device.assert_has_calls([call('device2-id'), call('device1-id')])

    def test_when_extension_is_updated_and_it_is_associated_with_other_lines(self):
        extension = {'id': 'extension-id', 'exten': '123', 'context': 'default'}
        line = {'id': 'line1-id', 'extensions': [extension]}
        user = {'uuid': '1234', 'lines': [line]}
        self.confd.users.get.return_value = {'lines': [line]}
        self.confd.extensions.get.return_value = {'lines': [{}, {}], 'exten': '234', 'context': 'default'}
        self.confd.extensions.create.return_value = extension

        self.service._update_user_lines(user)

        self.confd.lines.update.assert_called_once_with(line)
        self.confd.lines.return_value.remove_extension.assert_called_once_with(extension)
        self.confd.extensions.create.assert_called_once_with(extension)
        self.confd.lines.return_value.add_extension.assert_called_once_with(extension)
        self.confd.lines.delete.assert_not_called()
        self.confd.extensions.delete.assert_not_called()

    def test_when_extension_is_not_updated_and_it_is_associated_with_other_lines(self):
        extension = {'id': 'extension-id', 'exten': '123', 'context': 'default'}
        line = {'id': 'line1-id', 'extensions': [extension]}
        user = {'uuid': '1234', 'lines': [line]}
        self.confd.users.get.return_value = {'lines': [line]}
        self.confd.extensions.get.return_value = {'lines': [{}, {}], 'exten': '123', 'context': 'default'}
        self.confd.extensions.create.return_value = extension

        self.service._update_user_lines(user)

        self.confd.lines.update.assert_called_once_with(line)
        self.confd.extensions.update.assert_not_called()
        self.confd.lines.return_value.remove_extension.assert_not_called()
        self.confd.lines.return_value.add_extension.assert_not_called()
        self.confd.lines.delete.assert_not_called()
        self.confd.extensions.create.assert_not_called()
        self.confd.extensions.delete.assert_not_called()


class TestUserServiceCreateUserLines(unittest.TestCase):

    def setUp(self):
        self.confd = Mock()
        service.confd = self.confd
        wazo_admin_ui.helpers.service.confd = self.confd
        self.service = UserService()
        self.confd.lines.get.return_value = {'extensions': []}

    def test_when_line_with_no_id(self):
        user = {'uuid': '1234', 'lines': [{'id': ''}]}
        self.confd.lines.create.return_value = new_line = {'id': 'new-line-id'}

        self.service._create_user_lines(user)

        self.confd.lines.create.assert_called_once_with(new_line)
        self.confd.users.return_value.add_line.assert_called_once_with(new_line)
        self.confd.lines.update.assert_not_called()
        self.confd.lines.delete.assert_not_called()

    def test_when_line_with_id(self):
        line = {'id': 'line-id'}
        user = {'uuid': '1234', 'lines': [line]}

        self.service._create_user_lines(user)

        self.confd.users.return_value.add_line.assert_called_once_with(line)

    def test_when_line_with_endpoint_sip(self):
        user = {'uuid': '1234', 'lines': [{'endpoint_sip': {}}]}
        self.confd.lines.create.return_value = {'id': 'new-line-id'}
        self.confd.endpoints_sip.create.return_value = {'id': 'new-sip-id'}

        self.service._create_user_lines(user)

        self.confd.endpoints_sip.create.assert_called_once_with({})
        self.confd.lines.return_value.add_endpoint_sip.assert_called_once_with({'id': 'new-sip-id'})

    def test_when_line_with_endpoint_sccp(self):
        user = {'uuid': '1234', 'lines': [{'endpoint_sccp': {}}]}
        self.confd.lines.create.return_value = {'id': 'new-line-id'}
        self.confd.endpoints_sccp.create.return_value = {'id': 'new-sccp-id'}

        self.service._create_user_lines(user)

        self.confd.endpoints_sccp.create.assert_called_once_with({})
        self.confd.lines.return_value.add_endpoint_sccp.assert_called_once_with({'id': 'new-sccp-id'})

    def test_when_line_with_endpoint_custom(self):
        user = {'uuid': '1234', 'lines': [{'endpoint_custom': {}}]}
        self.confd.lines.create.return_value = {'id': 'new-line-id'}
        self.confd.endpoints_custom.create.return_value = {'id': 'new-custom-id'}

        self.service._create_user_lines(user)

        self.confd.endpoints_custom.create.assert_called_once_with({})
        self.confd.lines.return_value.add_endpoint_custom.assert_called_once_with({'id': 'new-custom-id'})

    def test_when_line_with_extension_and_no_existing_extension(self):
        extension = {'exten': '123', 'context': 'default'}
        user = {'uuid': '1234', 'lines': [{'endpoint_sip': {}, 'extensions': [extension]}]}
        self.confd.lines.create.return_value = {'id': 'new-line-id'}
        self.confd.extensions.create.return_value = {'id': 'new-extension-id'}
        self.confd.extensions.list.return_value = {'items': []}

        self.service._create_user_lines(user)

        self.confd.extensions.create.assert_called_once_with(extension)
        self.confd.lines.return_value.add_extension.assert_called_once_with({'id': 'new-extension-id'})

    def test_when_line_with_extension_and_existing_extension(self):
        extension = {'exten': '123', 'context': 'default'}
        user = {'uuid': '1234', 'lines': [{'endpoint_sip': {}, 'extensions': [extension]}]}
        self.confd.lines.create.return_value = {'id': 'new-line-id'}
        self.confd.extensions.list.return_value = {'items': [{'id': 'extension-id'}]}

        self.service._create_user_lines(user)

        self.confd.extensions.create.assert_not_called()
        self.confd.lines.return_value.add_extension.assert_called_once_with({'id': 'extension-id'})


class TestUserServiceUpdateDeviceAssociation(unittest.TestCase):

    def setUp(self):
        self.confd = Mock()
        service.confd = self.confd
        wazo_admin_ui.helpers.service.confd = self.confd
        self.service = UserService()
        self.confd.lines.get.return_value = {'device_id': None}

    def test_when_device_and_existing_device_with_same_id(self):
        device_id = 'device-id'
        self.confd.lines.get.return_value = {'device_id': device_id}

        self.service._update_device_association('line-id', device_id)

        self.confd.lines.return_value.add_device.assert_not_called()
        self.confd.lines.return_value.remove_device.assert_not_called()

    def test_when_no_device_and_no_existing_device(self):
        device_id = ''
        self.confd.lines.get.return_value = {'device_id': None}

        self.service._update_device_association('line-id', device_id)

        self.confd.lines.return_value.add_device.assert_not_called()
        self.confd.lines.return_value.remove_device.assert_not_called()

    def test_when_no_device_and_existing_device(self):
        device_id = None
        self.confd.lines.get.return_value = {'device_id': 'device-id'}

        self.service._update_device_association('line-id', device_id)

        self.confd.lines.return_value.add_device.assert_not_called()
        self.confd.lines.return_value.remove_device.assert_called_once_with('device-id')

    def test_when_device_and_no_existing_device(self):
        device_id = 'device-id'
        self.confd.lines.get.return_value = {'device_id': None}

        self.service._update_device_association('line-id', device_id)

        self.confd.lines.return_value.add_device.assert_called_once_with('device-id')
        self.confd.lines.return_value.remove_device.assert_not_called()

    def test_when_device_and_existing_device_with_different_id(self):
        device_id = 'device1-id'
        self.confd.lines.get.return_value = {'device_id': 'device2-id'}

        self.service._update_device_association('line-id', device_id)

        self.confd.lines.return_value.remove_device.assert_called_once_with('device2-id')
        self.confd.lines.return_value.add_device.assert_called_once_with('device1-id')
