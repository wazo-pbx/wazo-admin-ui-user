# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from flask_wtf import FlaskForm

from wtforms.fields import (FormField,
                            FieldList,
                            HiddenField,
                            SelectField,
                            SubmitField,
                            StringField)
from wtforms.fields.html5 import EmailField
from wtforms.validators import InputRequired

from wazo_admin_ui.helpers.destination import FallbacksForm, DestinationHiddenField


class LineForm(FlaskForm):
    line_id = HiddenField()
    extension_id = HiddenField()
    endpoint_sip_id = HiddenField()
    endpoint_sccp_id = HiddenField()
    endpoint_custom_id = HiddenField()
    protocol = SelectField(choices=[('sip', 'SIP'), ('sccp', 'SCCP'), ('custom', 'CUSTOM')])
    name = StringField()
    context = StringField()
    extension = StringField()
    device = StringField()
    position = StringField(default=1)


class UserForm(FlaskForm):
    firstname = StringField('Firstname', [InputRequired()])
    lastname = StringField('Lastname')
    extension = StringField('Extension')
    email = EmailField('Email')
    mobile_phone_number = StringField('Phone mobile')
    ring_seconds = StringField('Ring seconds')
    music_on_hold = StringField('Music on Hold')
    preprocess_subroutine = StringField('Subroutine')
    simultaneous_calls = StringField('Simultaneous calls')
    timezone = StringField('Timezone')
    userfield = StringField('User Field')
    description = StringField('Description')
    fallbacks = FormField(FallbacksForm)
    lines = FieldList(FormField(LineForm))
    submit = SubmitField('Submit')


class UserDestinationForm(FlaskForm):
    setted_value_template = '{user_firstname} {user_lastname}'

    user_id = SelectField('User', choices=[])
    ring_time = StringField('Ring time')
    user_firstname = DestinationHiddenField()
    user_lastname = DestinationHiddenField()
