FROM wazopbx/wazo-admin-ui

COPY . /usr/src/wazo-admin-ui-user
WORKDIR /usr/src/wazo-admin-ui-user

RUN python3 setup.py develop
