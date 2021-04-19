from setuptools import setup

setup(
    name='dynamite-remote',
    version='0.1.0',
    packages=[
        'dynamite_remote',
        'dynamite_remote/database',
    ],
    scripts=['scripts/dynamite-remote', 'scripts/bash_scripts/dynamite_remote_ssh_wrapper.sh'],
    url='https://dynamite.ai',
    license='GPL 3',
    author='Jamin Becker',
    author_email='jamin@dynamite.ai',
    description='Remotely manage DynamiteNSM nodes across your network environments.',
    include_package_data=True,
    install_requires=[
        'coloredlogs==15.0',
        'greenlet==1.0.0',
        'humanfriendly==9.1',
        'pexpect==4.8.0',
        'ptyprocess==0.7.0',
        'SQLAlchemy==1.4.7',
        'tabulate==0.8.9',
    ]
)