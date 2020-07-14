invoke-kubesae
=============

The kubesae library is an `invoke <http://docs.pyinvoke.org/en/stable/>`_ tasks library
to provide some basic management tasks for working with a kubernetes cluster.

License
-------

This invoke library is released under the BSD License.  See the `LICENSE
<https://github.com/caktus/invoke-kubesae/blob/master/LICENSE>`_ file for
more details.

Releases
--------

We attempt to not make changes that break backward-compatibility.
Nonetheless, you should *always* use a pinned version of this
repo to be safe.  Check the
`release history <RELEASES.rst>`_ before upgrading for
any notes or warnings.

Contributing
------------

If you think you've found a bug or are interested in contributing to
this project, check out `invoke-kubesae on Github
<https://github.com/caktus/invoke-kubesae>`_.

Development sponsored by `Caktus Consulting Group, LLC
<http://www.caktusgroup.com/services>`_.

Installation
------------

pip install into your virtualenv::

    $ pip install git+https://github.com/caktus/invoke-kubesae@X.Y.Z#egg=invoke-kubesae

Usage
-----

Invoke works from a ``tasks.py`` file usually found in the project root.

The following code snippet imports all of the the current collections,
then sets some configuration values for various tasks. See below for
more documentation on the configuration each task uses.


``tasks.py``::

    import invoke
    from colorama import init
    from kubesae import *


    init(autoreset=True)


    @invoke.task
    def staging(c):
        c.config.env = "staging"
        c.config.namespace = "myproject-staging"
        c.config.container_name = "myproject-web"


    ns = invoke.Collection()
    ns.add_collection(image)
    ns.add_collection(aws)
    ns.add_collection(deploy)
    ns.add_collection(pod)
    ns.add_task(staging)
    ns.configure(
        {
            "app": "appname",
            "aws": {
                "region": "us-west-2",
            },
            "repository": "123456789012.dkr.ecr.us-east-1.amazonaws.com/myproject",
            "run": {
                "echo": True,
                "pty": True,
            },
        }
    )


Now you can see all of the currently available tasks by running::

    $ inv -l

Build an image::

    $ inv image.build

Log in to the AWS docker registry::

    $ inv aws.docker-login

Push the image just built::

    $ inv image.push

Set up your kubectl context::

    $ inv aws.configure-eks-kubeconfig

Install Ansible roles::

    $ inv deploy.install

Deploy the same tag we just pushed::

    $ inv image.tag staging deploy.deploy

Task reference
==============

(In alphabetical order, and by collection)

AWS
---

configure-eks-kubeconfig
~~~~~~~~~~~~~~~~~~~~~~~~

    Obtain an EKS access token.

    Config:

        aws.region: Name of AWS region (default: us-east-1)

        cluster: Name of EKS cluster

docker-login
~~~~~~~~~~~~

    Obtain ECR credentials to use with docker login.

    Config:

        aws.region: Name of AWS region (default: us-east-1)

        repository: Name of docker repository, e.g. dockerhub.com/myproject.

Deploy
------

deploy
~~~~~~

    Deploy your k8s application. (Default)

    Prereq: deploy.install

    Config:

        env: Name of environment to deploy to

        tag: Image tag to deploy (default: same as default tag for build & push)

install
~~~~~~~

    Install ansible-galaxy requirements.yml.

Image
-----

build
~~~~~

    Build Docker image.  Tags with <tag> parameter and "latest".

    Config:

    Config:

        tag: tag to apply. (Will be generated from git branch/commit
        if not set).

push
~~~~

    Push docker image to remote repository. (Default)

    This command does the ``build`` and ``tag`` tasks before pushing.

    Config:

        repository: Name of docker repository, e.g. dockerhub.com/myproject.

        tag: tag to push. (Will be generated from git branch/commit
        if not set).

stop
~~~~

    Stops the deployable image in docker-compose

tag
~~~

    Generate tag based on local branch & commit hash.
    Set the config "tag" to the resulting tag.

up
~~~

    Brings up the deployable image locally in docker-compose for testing

write_docker_env_file
~~~~~~~~~~~~~~~~~~~~~

    Looks for a config variable named "docker_env_file_template_path", and if such
    a config variable exists, then it tries to run the commands in the file. The
    results of the commands are written into a file named ``docker_env_file``. The
    docker env template file should have 1 variable per line, each set to
    the command that would get that variable's value.
    For example::
     MOST_RECENT_GIT_REVISION=git rev-parse --short HEAD
     GIT_BRANCH=git rev-parse --abbrev-ref HEAD

    Running ``write_docker_env_file()`` on such a template will create a
    ``docker_env_file`` that will look like::
     MOST_RECENT_GIT_REVISION=jksd76hj
     GIT_BRANCH=my-current-git-branch

Pod
---

clean-debian
~~~~~~~~~~~~

    Removes the exited ephemeral debian pod

clean-migrations
~~~~~~~~~~~~~~~~

    Removes all migration jobs

debian
~~~~~~

    An ephemeral container with which to run sysadmin tasks on the cluster

fetch_namespace_var
~~~~~~~~~~~~~~~~~~~

    Takes a variable name that may be present on a running container. Queries the
    container for the value of that variable and returns it as a Result object.

get_db_dump
~~~~~~~~~~~

    Get a dump of an environment's database

restore_db_from_dump
~~~~~~~~~~~~

    Load a database dump file into an environment's database

shell
~~~~~

    Gives you a shell on the application pod. (Default)
