git-patch:
	rm -rf build
	rm -rf dist
	rm -rf unifr_api_epuck.egg-info
	git add -A
	@echo "commit message : "; \
	read MSG; \
	git commit -m',$$(MSG),'
	bumpversion patch 
	git push
	python3 setup.py sdist bdist_wheel
	python3 -m twine upload dist/*
	pip3 install unifr_api_epuck --upgrade

patch:
	rm -rf build
	rm -rf dist
	rm -rf unifr_api_epuck.egg-info
	python3 setup.py sdist bdist_wheel
	python3 -m twine upload dist/*
	pip3 install unifr_api_epuck --upgrade

git-minor:
	rm -rf build
	rm -rf dist
	rm -rf unifr_api_epuck.egg-info
	git add -A
	@echo "commit message : "; \
	read MSG; \
	git commit -m',$$(MSG),'
	bumpversion minor 
	git push
	python3 setup.py sdist bdist_wheel
	python3 -m twine upload dist/*
	pip3 uninstall unifr_api_epuck 

git-major:
	rm -rf build
	rm -rf dist
	rm -rf unifr_api_epuck.egg-info
	git add -A
	@echo "commit message : "; \
	read MSG; \
	git commit -m',$$(MSG),'
	bumpversion major 
	git push
	python3 setup.py sdist bdist_wheel
	python3 -m twine upload dist/*
	pip3 install unifr_api_epuck --upgrade

