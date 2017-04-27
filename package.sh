#!/bin/sh
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

case "$1" in
    build)
        python setup.py sdist --formats=zip
        ;;

    install)
        pip install sdist/wazo_admin_ui_user-*.zip
        cp etc/wazo-admin-ui/conf.d/user.yml /etc/wazo-admin-ui/conf.d
        systemctl restart wazo-admin-ui
        ;;

    uninstall)
        make uninstall
        ;;

    *)
        echo "$0 called with unknown argument '$1'" >&2
        exit 1
    ;;
esac
