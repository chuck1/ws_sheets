pkg=$(shell cat NAME.txt)

version=$(shell python3 -c 'import $(pkg);print($(pkg).__version__)')

test:
	@echo $(version)
	pipenv run python3 -m unittest $(pkg).tests -fv

upload: req
	@mkdir -p dist
	@rm -f dist/*whl
	python3 setup.py bdist_wheel
	twine upload dist/*whl

tmp:=$(shell mktemp)

req:
	pipenv run pip3 freeze > $(tmp)
	grep -vwe "git\+" $(tmp) > requirements.txt

