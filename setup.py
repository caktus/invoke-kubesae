# Always prefer setuptools over distutils
from setuptools import setup, find_packages


setup(
    name="invoke-kubesae",
    version="0.0.17",
    packages=find_packages(exclude=["tests"]),
    url="https://github.com/caktus/invoke-kubesae",
    author="Caktus Group",
    author_email="solutions@caktusgroup.com",
    description="An invoke tasks library to manage a kubernetes project.",
    long_description=open("README.rst").read(),
    long_description_content_type='text/x-rst',
    license="BSD",
    include_package_data=True,
    install_requires=[
        "boto3>=1.16",
        "invoke>=1.4",
        "colorama>=0.4",
        "ansible>=2.9",
    ],
    python_requires=">=3.5",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Build Tools",
    ],
)
