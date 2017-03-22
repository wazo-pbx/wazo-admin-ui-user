# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from flask_wtf import FlaskForm

from wtforms.fields import (FormField,
                            IntegerField,
                            SelectField,
                            SubmitField,
                            TextField)
from wtforms.fields.html5 import EmailField
from wtforms.validators import InputRequired

from wazo_admin_ui.helpers.destination import FallbacksForm, DestinationHiddenField


class UserForm(FlaskForm):
    firstname = TextField('Firstname', [InputRequired()])
    lastname = TextField('Lastname')
    extension = TextField('Extension')
    email = EmailField('Email')
    mobile_phone_number = TextField('Phone mobile')
    ring_seconds = TextField('Ring seconds')
    music_on_hold = TextField('Music on Hold')
    preprocess_subroutine = TextField('Subroutine')
    simultaneous_calls = TextField('Simultaneous calls')
    timezone = TextField('Timezone')
    userfield = TextField('User Field')
    description = TextField('Description')
    fallbacks = FormField(FallbacksForm)
    submit = SubmitField('Submit')


class UserDestinationForm(FlaskForm):
    setted_value_template = '{user_firstname} {user_lastname}'

    user_id = SelectField('User', choices=[])
    ring_time = IntegerField('Ring time')
    user_firstname = DestinationHiddenField()
    user_lastname = DestinationHiddenField()
