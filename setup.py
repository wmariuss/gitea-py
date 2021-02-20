from setuptools import setup

setup(
    name='giteapy',
    version='1.3.1',
    author='Marius Stanca',
    author_email=['me@mariuss.me', 'me@marius.xyz'],
    url='http://mariuss.me',
    license='MIT',
    description='Manage organizations, teams and permissions in gitea',
    packages=['giteapy'],
    long_description=open('README.md').read(),
    include_package_data=True,
    package_data={'': ['README.md']},
    install_requires=['click>=7.0', 'cerberus==1.2', 'pyyaml', 'requests==2.20.1', 'termcolor==1.1.0'],
    extras_require={
        'click': ['click>=7.0']},
    classifiers=[
        'Environment :: Tools Environment',
        'Intended Audience :: Operations',
        'License :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.x',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    entry_points='''
        [console_scripts]
        giteapy=giteapy.cli:cli
    '''
)
