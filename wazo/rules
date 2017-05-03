#!/bin/sh
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

case "$1" in
    build)
        python setup.py bdist_egg
        ;;

    install)
        easy_install dist/wazo_admin_ui_user-*-py2.7.egg
        cp etc/wazo-admin-ui/conf.d/user.yml /etc/wazo-admin-ui/conf.d
        systemctl restart wazo-admin-ui
        ;;

    uninstall)
        rm -rf /usr/local/lib/python2.7/dist-packages/wazo_admin_ui_user-*-py2.7.egg
        rm -f /etc/wazo-admin-ui/conf.d/user.yml
        systemctl restart wazo-admin-ui
        ;;

    *)
        echo "$0 called with unknown argument '$1'" >&2
        exit 1
    ;;
esac
