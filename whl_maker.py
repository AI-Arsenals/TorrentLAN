from setuptools import setup, find_packages

setup(
    name='TorrentLAN',
    version='1.0.0',
    author=['Prakhar Gupta', 'Sameer Sharma'],
    author_email=['gupta.99@iitj.ac.in', 'sharma.131@iitj.ac.in'],
    packages=find_packages(),
    install_requires=[
        'netifaces==0.11.0',
        'termcolor==2.3.0',
        'requests==2.31.0',
        # Add any other project dependencies here
    ],
    setup_requires=[
        'setuptools>=42',
        'wheel'
    ],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 2',
        'Operating System :: OS Independent',
    ],
)

# # build command
# python setup.py bdist_wheel --universal --python-tag=py2.py3 --plat-name=any

