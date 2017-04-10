# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+


from wtforms.fields import (FormField,
                            FieldList,
                            HiddenField,
                            SelectField,
                            SubmitField,
                            StringField)
from wtforms.fields.html5 import EmailField
from wtforms.validators import InputRequired

from wazo_admin_ui.helpers.destination import FallbacksForm, DestinationHiddenField
from wazo_admin_ui.helpers.form import BaseForm


class LineForm(BaseForm):
    line_id = HiddenField()
    extension_id = HiddenField()
    endpoint_sip_id = HiddenField()
    endpoint_sccp_id = HiddenField()
    endpoint_custom_id = HiddenField()
    protocol = SelectField(choices=[('sip', 'SIP'), ('sccp', 'SCCP'), ('custom', 'CUSTOM'), ('webrtc', 'SIP (webrtc)')])
    name = StringField()
    context = SelectField(choices=[])
    extension = SelectField(choices=[])
    device = SelectField(choices=[])
    device_mac = HiddenField()
    position = StringField(default=1)


class UserForwardForm(BaseForm):
    noanswer = StringField('No answer')
    busy = StringField('Busy')
    unconditional = StringField('Unconditional')


class UserServiceForm(BaseForm):
    dnd = StringField('Dnd')
    incallfilter = StringField('Incall filter')


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
