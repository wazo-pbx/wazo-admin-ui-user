#!/bin/sh
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

case "$1" in
    build)
        make build
        ;;

    install)
        make install
        ;;

    uninstall)
        make uninstall
        ;;

    *)
        echo "$0 called with unknown argument '$1'" >&2
        exit 1
    ;;
esac
