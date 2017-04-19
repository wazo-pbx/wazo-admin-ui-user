# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+


from wtforms.fields import (BooleanField,
                            FormField,
                            FieldList,
                            HiddenField,
                            SelectField,
                            SubmitField,
                            StringField)
from wtforms.fields.html5 import EmailField
from wtforms.validators import InputRequired

from wazo_admin_ui.helpers.destination import FallbacksForm, DestinationHiddenField
from wazo_admin_ui.helpers.form import BaseForm


class ExtensionForm(BaseForm):
    id = HiddenField()
    exten = SelectField(choices=[])


class LineForm(BaseForm):
    id = HiddenField()
    context = SelectField(choices=[])
    endpoint_sip_id = HiddenField()
    endpoint_sccp_id = HiddenField()
    endpoint_custom_id = HiddenField()
    protocol = SelectField(choices=[('sip', 'SIP'), ('sccp', 'SCCP'), ('custom', 'CUSTOM'), ('webrtc', 'SIP (webrtc)')])
    extensions = FieldList(FormField(ExtensionForm), min_entries=1)
    name = StringField()
    device = SelectField(choices=[])
    position = StringField(default=1)


class BusyForwardForm(BaseForm):
    enabled = BooleanField('Busy', default=False)
    destination = StringField('Destination')


class NoAnswerForwardForm(BaseForm):
    enabled = BooleanField('No answer', default=False)
    destination = StringField('Destination')


class UnconditionalForwardForm(BaseForm):
    enabled = BooleanField('Unconditional', default=False)
    destination = StringField('Destination')


class UserForwardForm(BaseForm):
    busy = FormField(BusyForwardForm)
    noanswer = FormField(NoAnswerForwardForm)
    unconditional = FormField(UnconditionalForwardForm)


class DNDServiceForm(BaseForm):
    enabled = BooleanField('Do not disturb', default=False)


class IncallFilterServiceForm(BaseForm):
    enabled = BooleanField('Incall filtering', default=False)


class UserServiceForm(BaseForm):
    dnd = FormField(DNDServiceForm)
    incallfilter = FormField(IncallFilterServiceForm)


class UserForm(BaseForm):
    firstname = StringField('Firstname', [InputRequired()])
    lastname = StringField('Lastname')
    username = StringField('Username')
    password = StringField('Password')
    extension = StringField('Extension')
    email = EmailField('Email')
    mobile_phone_number = StringField('Phone mobile')
    ring_seconds = StringField('Ring seconds')
    music_on_hold = SelectField('Music On Hold', choices=[])
    preprocess_subroutine = StringField('Subroutine')
    simultaneous_calls = StringField('Simultaneous calls')
    timezone = StringField('Timezone')
    userfield = StringField('User Field')
    description = StringField('Description')
    fallbacks = FormField(FallbacksForm)
    forwards = FormField(UserForwardForm)
    services = FormField(UserServiceForm)
    lines = FieldList(FormField(LineForm))
    submit = SubmitField('Submit')


class UserDestinationForm(BaseForm):
    setted_value_template = u'{user_firstname} {user_lastname}'

    user_id = SelectField('User', choices=[])
    ring_time = StringField('Ring time')
    user_firstname = DestinationHiddenField()
    user_lastname = DestinationHiddenField()
