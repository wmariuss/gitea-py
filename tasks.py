import os
from invoke import task


@task
def clean(c):
    py_files = [
        'build',
        'dist',
        '__pycache__',
        '*.pyc',
        '*.egg-info',
        '*.whl',
        '*.pex'
    ]
    print("Cleaning up...")
    for file in py_files:
        c.run("rm -rf {}".format(file))


@task
def upload(c):
    c.run("python setup.py sdist upload -r pypicloud")
