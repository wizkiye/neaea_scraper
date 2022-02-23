from setuptools import setup

setup(
    name='neaea',
    version='1.0.0',
    url='https://github.com/wizkiye/neaea_scraper',
    license='MIT',
    author='https://github.com/wizkiye',
    author_email='wizkiye@gmail.com',
    description='Neaea Exam Result Scraper',
    install_requires=['requests', 'motor', 'rich'],
    packages=['neaea']
)
