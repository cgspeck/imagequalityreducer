from setuptools import setup

with open('requirements.txt') as f:
    required = f.read().splitlines()

with open('requirements-test.txt') as f:
    required_test = f.read().splitlines()

setup(
    name='Image Quality Reducer',
    description='''
    Reduce images to desired file size
    ''',
    version='0.9.1',
    author='Chris Speck',
    author_email='cgspeck@gmail.com',
    url='http://www.chrisspeck.com/',
    packages=['qualityreducer'],
    entry_points={
        'console_scripts': [
            'qualityreducer = qualityreducer.utilrunner:main'
        ]
    },
    install_requires=required,
    extras_require={
        'tests': required_test
    }
)
