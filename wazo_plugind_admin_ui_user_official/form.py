# Copyright 2017-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+


from flask_babel import lazy_gettext as l_
from wtforms.fields import (BooleanField,
                            FormField,
                            FieldList,
                            HiddenField,
                            SelectField,
                            SelectMultipleField,
                            SubmitField,
                            StringField)
from wtforms.fields.html5 import EmailField, IntegerField
from wtforms.validators import InputRequired, Length, NumberRange

from wazo_admin_ui.helpers.destination import FallbacksForm, DestinationHiddenField
from wazo_admin_ui.helpers.form import BaseForm
from wazo_admin_ui.helpers.funckey import FuncKeyDestinationField


class ExtensionForm(BaseForm):
    id = HiddenField()
    exten = SelectField(choices=[])


class LineForm(BaseForm):
    id = HiddenField()
    context = SelectField(choices=[])
    endpoint_sip_id = HiddenField()
    endpoint_sccp_id = HiddenField()
    endpoint_custom_id = HiddenField()
    protocol = SelectField(choices=[('sip', l_('SIP')),
                                    ('sccp', l_('SCCP')),
                                    ('custom', l_('CUSTOM')),
                                    ('webrtc', l_('SIP (webrtc)'))])
    extensions = FieldList(FormField(ExtensionForm), min_entries=1)
    name = StringField()
    device = SelectField(choices=[])
    position = IntegerField(default=1, validators=[NumberRange(min=1), InputRequired()])


class BusyForwardForm(BaseForm):
    enabled = BooleanField(l_('Busy'), default=False)
    destination = StringField(l_('Destination'), [Length(max=128)])


class NoAnswerForwardForm(BaseForm):
    enabled = BooleanField(l_('No answer'), default=False)
    destination = StringField(l_('Destination'), [Length(max=128)])


class UnconditionalForwardForm(BaseForm):
    enabled = BooleanField(l_('Unconditional'), default=False)
    destination = StringField(l_('Destination'), [Length(max=128)])


class UserForwardForm(BaseForm):
    busy = FormField(BusyForwardForm)
    noanswer = FormField(NoAnswerForwardForm)
    unconditional = FormField(UnconditionalForwardForm)


class DNDServiceForm(BaseForm):
    enabled = BooleanField(l_('Do not disturb'), default=False)


class IncallFilterServiceForm(BaseForm):
    enabled = BooleanField(l_('Incall filtering'), default=False)


class UserServiceForm(BaseForm):
    dnd = FormField(DNDServiceForm)
    incallfilter = FormField(IncallFilterServiceForm)


class CtiProfileForm(BaseForm):
    id = SelectField(l_('CTI Profile'), choices=[])
    name = HiddenField()


class GroupForm(BaseForm):
    id = HiddenField()
    name = HiddenField()


class FuncKeyTemplateKeysForm(BaseForm):
    id = HiddenField()
    label = StringField(l_('Label'), [Length(max=128)])
    digit = IntegerField(validators=[InputRequired()])
    destination = FuncKeyDestinationField()
    blf = BooleanField(l_('BLF'), default=True)
    submit = SubmitField()


class UserForm(BaseForm):
    firstname = StringField(l_('Firstname'), [InputRequired(), Length(max=128)])
    lastname = StringField(l_('Lastname'), [Length(max=128)])
    username = StringField(l_('Username'), [Length(min=2, max=254)])
    password = StringField(l_('Password'), [Length(min=4, max=64)])
    email = EmailField(l_('Email'), [Length(max=254)])
    mobile_phone_number = StringField(l_('Phone mobile'), [Length(max=80)])
    ring_seconds = IntegerField(l_('Ring seconds'), [NumberRange(min=0, max=60)])
    music_on_hold = SelectField(l_('Music On Hold'), choices=[])
    preprocess_subroutine = StringField(l_('Subroutine'), [Length(max=39)])
    simultaneous_calls = IntegerField(l_('Simultaneous calls'), [NumberRange(min=1, max=20)])
    timezone = StringField(l_('Timezone'), [Length(max=254)])
    userfield = StringField(l_('User Field'), [Length(max=128)])
    description = StringField(l_('Description'))
    fallbacks = FormField(FallbacksForm)
    forwards = FormField(UserForwardForm)
    services = FormField(UserServiceForm)
    lines = FieldList(FormField(LineForm))
    cti_profile = FormField(CtiProfileForm)
    group_ids = SelectMultipleField(l_('Groups'), choices=[])
    groups = FieldList(FormField(GroupForm))
    funckeys = FieldList(FormField(FuncKeyTemplateKeysForm))
    submit = SubmitField(l_('Submit'))


class UserDestinationForm(BaseForm):
    set_value_template = '{user_firstname} {user_lastname}'

    user_id = SelectField(l_('User'), choices=[], validators=[InputRequired()])
    ring_time = IntegerField(l_('Ring time'), [NumberRange(min=0)])
    user_firstname = DestinationHiddenField()
    user_lastname = DestinationHiddenField()


class UserFuncKeyDestinationForm(BaseForm):
    set_value_template = '{user_firstname} {user_lastname}'

    user_id = SelectField(l_('User'), [InputRequired()], choices=[])
    user_firstname = DestinationHiddenField()
    user_lastname = DestinationHiddenField()
