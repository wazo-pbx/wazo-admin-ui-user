# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from flask_wtf import FlaskForm

from wtforms.fields import SubmitField
from wtforms.fields import TextField
from wtforms.fields import BooleanField

from wtforms.validators import InputRequired
from wtforms.validators import Optional


class UserForm(FlaskForm):
    firstname = TextField('Firstname', [InputRequired()])
    lastname = TextField('Lastname')
    submit = SubmitField('Submit')
