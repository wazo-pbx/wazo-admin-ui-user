# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from flask_wtf import FlaskForm

from wtforms.fields import (FormField,
                            IntegerField,
                            SelectField,
                            SubmitField,
                            StringField)
from wtforms.fields.html5 import EmailField
from wtforms.validators import InputRequired

from wazo_admin_ui.helpers.destination import FallbacksForm, DestinationHiddenField


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
    submit = SubmitField('Submit')


class UserDestinationForm(FlaskForm):
    setted_value_template = '{user_firstname} {user_lastname}'

    user_id = SelectField('User', choices=[])
    ring_time = IntegerField('Ring time')
    user_firstname = DestinationHiddenField()
    user_lastname = DestinationHiddenField()
