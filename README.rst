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
this project, check out `invoke-kubsae on Github
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

The following code snippet imports all of the the current collections.


``tasks.py``::

    import invoke
    from colorama import init
    from kubesae import *


    init(autoreset=True)


    @invoke.task
    def staging(c):
        c.config.env = "staging"


    ns = invoke.Collection()
    ns.add_collection(image)
    ns.add_collection(aws)
    ns.add_collection(deploy)
    ns.add_collection(pod)
    ns.add_task(staging)
    ns.configure({"run": {"echo": True}})


Now you can see all of the currently available tasks by running::

    $ inv -l



Task reference
==============

(In alphabetical order, and by collection)

AWS
---

configure-eks-kubeconfig
~~~~~~~~~~~~~~~~~~~~~~~~

    Obtain an EKS access token.

docker-login
~~~~~~~~~~~~

    Obtain ECR credentials to use with docker login.

Deploy
------

deploy
~~~~~~

    Deploy your k8s application. (Default)

install
~~~~~~~

    Install ansible-galaxy requirements.yml.

Image
-----

build
~~~~~

    Builds the docker image using docker-compose.

push
~~~~

    Push docker image to remote repository. (Default)
    
    This command does the ``build`` and ``tag`` tasks before pushing.

stop
~~~~

    Stops the deployable image

tag
~~~

    Generate tag based on local branch & commit hash

up 
~~~

    Brings up the deployable image locally for testing

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

shell
~~~~~

    Gives you a shell on the application pod. (Default)




