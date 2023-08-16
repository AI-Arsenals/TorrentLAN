from setuptools import setup, find_packages

setup(
    name='TorrentLAN',
    version='1.0.0',
    author=['Prakhar Gupta', 'Sameer Sharma'],
    author_email=['gupta.99@iitj.ac.in', 'sharma.131@iitj.ac.in'],
    packages=find_packages(),
    install_requires=[
        'psutil==5.9.5',
        'termcolor==2.3.0',
        'requests==2.31.0',
        'SQLAlchemy==2.0.19',
        'Django==4.2.3',
        'djangorestframework==3.14.0',
        'django-cors-headers==3.8.0',

        # Add any other project dependencies here
    ],
    setup_requires=[
        'setuptools>=42',
        'wheel'
    ],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
)

# # build command
# python ./whl_maker.py bdist_wheel --universal --python-tag=py3 --plat-name=any

