 rm -r dist/
 python setup.py sdist
 twine upload dist/*
