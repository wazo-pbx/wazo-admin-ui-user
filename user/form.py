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
from wtforms.fields.html5 import EmailField, IntegerField
from wtforms.validators import InputRequired, Length, NumberRange

from wazo_admin_ui.helpers.destination import FallbacksForm, DestinationHiddenField
from wazo_admin_ui.helpers.form import BaseForm


class ExtensionForm(BaseForm):
    id = HiddenField()
    exten = SelectField(choices=[])


class LineForm(BaseForm):
    id = HiddenField()
    context = SelectField(choices=[], validators=[InputRequired()])
    endpoint_sip_id = HiddenField()
    endpoint_sccp_id = HiddenField()
    endpoint_custom_id = HiddenField()
    protocol = SelectField(choices=[('sip', 'SIP'), ('sccp', 'SCCP'), ('custom', 'CUSTOM'), ('webrtc', 'SIP (webrtc)')])
    extensions = FieldList(FormField(ExtensionForm), min_entries=1)
    name = StringField()
    device = SelectField(choices=[])
    position = IntegerField(default=1, validators=[NumberRange(min=1), InputRequired()])


class BusyForwardForm(BaseForm):
    enabled = BooleanField('Busy', default=False)
    destination = StringField('Destination', [Length(max=128)])


class NoAnswerForwardForm(BaseForm):
    enabled = BooleanField('No answer', default=False)
    destination = StringField('Destination', [Length(max=128)])


class UnconditionalForwardForm(BaseForm):
    enabled = BooleanField('Unconditional', default=False)
    destination = StringField('Destination', [Length(max=128)])


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
    firstname = StringField('Firstname', [InputRequired(), Length(max=128)])
    lastname = StringField('Lastname', [Length(max=128)])
    username = StringField('Username', [Length(min=2, max=254)])
    password = StringField('Password', [Length(min=4, max=64)])
    email = EmailField('Email', [Length(max=254)])
    mobile_phone_number = StringField('Phone mobile', [Length(max=80)])
    ring_seconds = IntegerField('Ring seconds', [NumberRange(min=0, max=60)])
    music_on_hold = SelectField('Music On Hold', choices=[])
    preprocess_subroutine = StringField('Subroutine', [Length(max=39)])
    simultaneous_calls = IntegerField('Simultaneous calls', [NumberRange(min=1, max=20)])
    timezone = StringField('Timezone', [Length(max=254)])
    userfield = StringField('User Field', [Length(max=128)])
    description = StringField('Description')
    fallbacks = FormField(FallbacksForm)
    forwards = FormField(UserForwardForm)
    services = FormField(UserServiceForm)
    lines = FieldList(FormField(LineForm))
    submit = SubmitField('Submit')


class UserDestinationForm(BaseForm):
    setted_value_template = u'{user_firstname} {user_lastname}'

    user_id = SelectField('User', choices=[], validators=[InputRequired()])
    ring_time = IntegerField('Ring time', [NumberRange(min=0)])
    user_firstname = DestinationHiddenField()
    user_lastname = DestinationHiddenField()
