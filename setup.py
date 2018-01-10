from setuptools import setup

setup(
    name='python-songpal',

    version='0.0.3',
    description="Python library for interfacing with Sony's Songpal devices",
    url='https://github.com/rytilahti/python-songpal',

    author='Teemu Rytilahti',
    author_email='tpr@iki.fi',

    license='GPLv3',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
    ],

    keywords='sony songpal soundbar',

    packages=['songpal'],

    install_requires=['click', 'websockets', 'upnpclient', 'attrs'],
    python_requires='>=3.5',
    entry_points={
        'console_scripts': [
            'songpal=songpal.main:cli',
        ],
    },
)
