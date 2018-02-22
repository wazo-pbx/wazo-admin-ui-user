#!/usr/bin/env python3
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from setuptools import find_packages
from setuptools import setup
from setuptools.command.egg_info import egg_info as _egg_info
from babel.messages import frontend as babel
from babel.messages.catalog import Catalog as _Catalog

PROJECT = 'wazo-admin-ui-user'

DEFAULT_HEADER = u"""\
# Translations template for {PROJECT}.
# Copyright (C) 2018 The Wazo Authors  (see the AUTHORS file)
# This file is distributed under the same license as the
# {PROJECT} project.
# Wazo Dev Team <dev@wazo.community>, 2018.
#""".format(PROJECT=PROJECT)


class Catalog(_Catalog):
    def __init__(self,
                 project=PROJECT,
                 copyright_holder='The Wazo Authors  (see the AUTHORS file)',
                 msgid_bugs_address='dev@wazo.community',
                 last_translator='Wazo Authors <dev@wazo.community>',
                 language_team='en <dev@wazo.community>', **kwargs):
        super().__init__(header_comment=DEFAULT_HEADER,
                         project=project, copyright_holder=copyright_holder,
                         msgid_bugs_address=msgid_bugs_address, last_translator=last_translator,
                         language_team=language_team, fuzzy=False, **kwargs)


babel.Catalog = Catalog


class egg_info(_egg_info):
    def run(self):
        self.run_command('compile_catalog')
        _egg_info.run(self)


setup(
    name=PROJECT,
    version='0.1',

    description='Wazo Admin User',

    author='Wazo Authors',
    author_email='dev@wazo.community',

    url='http://wazo.community',

    packages=find_packages(),
    setup_requires=['Babel'],
    install_requires=['Babel'],
    include_package_data=True,
    zip_safe=False,

    cmdclass={
        'egg_info': egg_info,
        'compile_catalog': babel.compile_catalog,
        'extract_messages': babel.extract_messages,
        'init_catalog': babel.init_catalog,
        'update_catalog': babel.update_catalog
    },

    entry_points={
        'wazo_admin_ui.plugins': [
            'user = wazo_plugind_admin_ui_user_official.plugin:Plugin',
        ]
    }
)
