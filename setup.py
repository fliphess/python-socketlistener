import os
from distutils.core import setup

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))
setup(
    name='python-socketlistener',
    version='0.1',
    url='https://github.com/fliphess/python-socketlistener',
    author='Flip Hess',
    author_email='flip@fliphess.com',
    description='A simple socket server for sending encrypted data over udp from one to another',
    packages=['python_socketlistener'],
)
