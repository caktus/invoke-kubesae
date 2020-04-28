# Always prefer setuptools over distutils
from setuptools import setup

setup(
    name='invoke-kubsae',
    version='0.0.1',
    packages=[
        'invocations',
    ],
    url='https://github.com/caktus/invoke-kubsae',
    author='Caktus Group',
    author_email='',
    description='',
    install_requires=[
        'invoke>=1.4',
        'colorama>=0.4',
        'ansible>=2.9',
    ],
    python_requires='>=3.5',
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
    ]
)
