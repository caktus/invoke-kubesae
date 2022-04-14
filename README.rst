invoke-kubesae
==============

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

    $ pip install invoke-kubesae

Usage
-----

Invoke works from a ``tasks.py`` file usually found in the project root.

The following code snippet imports all of the the current collections to show an
example for supporting AWS, then sets some configuration values for various tasks.
Note that GCP is also supported in the ``providers.gcp`` module, and works similarly
to the ``providers.aws`` module. See below for more documentation on the
configuration each task uses.


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
                "profile_name": "my-aws-profile",  # a profile from .aws/credentials
            },
            "repository": "123456789012.dkr.ecr.us-east-1.amazonaws.com/myproject",
            "run": {
                "echo": True,
                "pty": True,
            },
        }
    )

.. note::
   The ``profile_name`` in the config above is only used when you run custom playbooks,
   not the main deploy playbook. It is used because boto doesn't work well with
   AssumedRoles, so if your playbook needs an AssumedRole we have to convert the role
   credentials to standard AWS access_key/secret credentials and we use the profile above
   to do that. This assumes that all devs in your project are using the same profile
   name, but if you want to customize it, you can create a project-level task to
   customize it.


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

sync-media
~~~~~~~~~~

    Syncs a media bucket between two namespaces (e.g. `production` to `staging`, or
    `staging` to `local`).

Deploy
------

deploy
~~~~~~

    Deploy your k8s application. (Default)

    WARNING: if you are running this in CI, make sure to set `--verbosity=0` to prevent
    environment variables from being logged in plain text in the CI console.

    Prereq: deploy.install

    Config:

        env: The target ansible host ("staging", "production", etc ...)

        tag: Image tag to deploy (default: same as default tag for build & push)

        verbosity: integer level of verbosity from 0 to 4 (most verbose)

install
~~~~~~~

    Install ansible-galaxy requirements.yml.

playbook
~~~~~~~~

    Run a specified Ansible playbook, located in the ``deploy/`` directory. Used to run
    a different playbook than the default playbook.

    WARNING: if you are running this in CI, make sure to set `--verbosity=0` to prevent
    environment variables from being logged in plain text in the CI console.

    Config:

        name: The name of the Ansible playbook to run, including the extension

        extra: Additional command line arguments to ansible-playbook

        verbosity: integer level of verbosity from 0 to 4 (most verbose)

GCP
---

configure-gcp-kubeconfig
~~~~~~~~~~~~~~~~~~~~~~~~

    Authenticate into GCP to get credentials for the cluster.

    Config:

        app: Name of the project in GCP

        gcp.region: Name of GCP region (default: us-east1)

        cluster: Name of cluster in GCP (default config.cluster)

docker-login
~~~~~~~~~~~~

    Authenticate into GCP, and configure Docker.

    Config:

        app: Name of the project in GCP

        repository: Name of docker repository, e.g. us.gcr.io/myproject/myproject

sync-media
~~~~~~~~~~

    Syncs a media bucket between two namespaces (e.g. `production` to `staging`, or
    `staging` to `local`).

Image
-----

build
~~~~~

    Build Docker image.  Tags with <tag> parameter and "latest".

    Config:

        tag: tag to apply. (Will be generated from git branch/commit
        if not set).

    Params:

        tag: tag to apply. (Will be generated from git branch/commit
        if not set).

        dockerfile: A non-standard Dockerfile location and/or name

push
~~~~

    Push docker image to remote repository. (Default)

    This command does the ``build`` and ``tag`` tasks before pushing.

    Config:

        repository: Name of docker repository, e.g. dockerhub.com/myproject.

        tag: tag to push. (Will be generated from git branch/commit
        if not set).

    Params:

        tag: tag to apply. (Will be generated from git branch/commit
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


Info
----

print-ansible-vars
~~~~~~~~~~~~~~~~~~

    A command to inspect any ansible variable by environment. If no variable is specified then it will
    print out the current k8s environment variables.

    Params:
        c (invoke.Context): The current invoke context.
        var (string, optional): The ansible variable you want to expose. Defaults to None.
        yaml (string, optional): An ansible path. Defaults to None.
        pty (bool, optional): If piping the output to another command you might need this to be False. Defaults to True.
        hide (bool, optional): If you don't want the results to print to the console set to "out". Defaults to False.

pod-stats
~~~~~~~~~

    Report total pods vs pod capacity in a cluster.

Pod
---

clean-collectstatic
~~~~~~~~~~~~~~~~~~~

    Removes all collectstatic pods

    Config:

        namespace: the k8s namespace that will be cleaned

clean-debian
~~~~~~~~~~~~

    Clears away the old debian pod so a new one may live.

clean-migrations
~~~~~~~~~~~~~~~~

    Removes all migration jobs

    Config:

        namespace: the k8s namespace that will be cleaned

debian
~~~~~~

    An ephemeral container with which to run sysadmin tasks on the cluster

fetch_namespace_var
~~~~~~~~~~~~~~~~~~~

    Takes a variable name that may be present on a running container. Queries the
    container for the value of that variable and returns it as a Result object.

    Config:

        namespace: the k8s namespace that will be cleaned

        container_name: Name of the Docker container.

    Params:

        fetch_var (str): An environment variable expected on the target container

        hide (bool, optional): Hides the stdout if True. Defaults to False.

get_db_dump
~~~~~~~~~~~

    Get a dump of an environment's database

    Config:

        namespace: the k8s namespace that will be cleaned

        container_name: Name of the Docker container.

    Params:

        db_var (str): The variable name that the database connection is stored in.

        filename (string, optional): A filename to store the dump. If None, will default to {namespace}_database.dump.

restore_db_from_dump
~~~~~~~~~~~~~~~~~~~~

    Load a database dump file into an environment's database

    Config:

        namespace: the k8s namespace that will be cleaned

        container_name: Name of the Docker container.

    Params:

        db_var (str): The variable the database connection is stored in.

        filename (string): An filename of the dump to restore.

shell
~~~~~

    Gives you a shell on the application pod. (Default)

    Config:

        container_name: Name of the Docker container.

Utils
-----

get_backup_from_hosting
~~~~~~~~~~~~~~~~~~~~~~~

    Downloads a backup from the caktus hosting services bucket

    Params:

        c (invoke.Context): the running context
        latest (str, optional): Gets the latest backup from the specified temporal period. Defaults to "daily". Options are "daily", "weekly", "monthly", "yearly"
        profile (str, optional): The AWS profile to allow access to the s3 bucket. DEFAULT: "caktus"
        backup_name(str, optional): A specific backup filename.
        list(bool, optional): If set, will list the contents of the bucket for the projects folder and exit.

    The use of this task requires the addition of `hosting_services_backup_folder` to your `tasks.py`
    configuration:

        ns.configure({"hosting_services_backup_folder": "<PROJECT_FOLDER>",})

count_backups
~~~~~~~~~~~~~

    Sorts the backups generated with caktus-hosting-services cronjob and prints the number found of each type.

    Params:

        `c` (invoke.Context): The running context
        `bucket_identifier` (str, optional): The name of the bucket that holds the backups. DEFAULT: `caktus-hosting-services-backups`
        `profile` (str, optional): The AWS profile with list access to the bucket. DEFAULT: `caktus`
        `extra_schedules` (str, optional): A comma delimited string with each additional schedule name no spaces. EXAMPLE: `'every2hours,every-hour,every-thursday'`

list_backup_schedules
~~~~~~~~~~~~~~~~~~~~~

    Lists the backup schedules found in a project's hosting bucket.

    Params:

        `c` (invoke.Context): The running context
        `bucket_identifier` (str, optional): The name of the bucket that holds the backups. DEFAULT: `caktus-hosting-services-backups`
        `profile` (str, optional): The AWS profile with list access to the bucket. DEFAULT: `caktus`
