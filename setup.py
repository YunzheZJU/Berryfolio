from setuptools import setup

setup(
    name='berryfolio',
    packages=['berryfolio'],
    include_package_data=True,
    install_requires=[
        'flask',
        'flask_uploads',
        'WTForms',
        'flask_wtf',
        'Pillow',
    ],
)