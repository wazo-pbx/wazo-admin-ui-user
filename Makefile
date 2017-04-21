install:
	python setup.py install
	cp etc/wazo-admin-ui/conf.d/user.yml /etc/wazo-admin-ui/conf.d
	systemctl restart wazo-admin-ui

uninstall:
	pip uninstall --yes wazo-admin-ui-user
	rm /etc/wazo-admin-ui/conf.d/user.yml
	systemctl restart wazo-admin-ui
