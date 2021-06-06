update:
	rm -rf build
	rm -rf dist
	rm -rf unifr_api_epuck.egg-info
	python3 setup.py sdist bdist_wheel
	python3 -m twine upload dist/*  

service:
	sudo scp pi-puck-conf/systemctl/pipuck-start.service /etc/systemd/system
	sudo systemctl enable pipuck-start.service
