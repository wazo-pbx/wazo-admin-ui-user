# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from flask_wtf import FlaskForm

from wtforms.fields import SubmitField
from wtforms.fields import TextField
from wtforms.fields import BooleanField
from wtforms.fields.html5 import EmailField

from wtforms.validators import InputRequired
from wtforms.validators import Optional


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
    submit = SubmitField('Submit')
