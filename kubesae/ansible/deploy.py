import os

import invoke


@invoke.task
def install_requirements(c):
    """Install ansible-galaxy requirements.yml

    Usage: inv deploy.install
    """
    req_file = "requirements.yml" if os.path.exists("deploy/requirements.yml") else "requirements.yaml"
    with c.cd("deploy/"):
        c.run(f"ansible-galaxy install -f -r '{req_file}' -p roles/")


def get_verbosity_flag(verbosity):
    """
    Given an integer, return a string with that number of `v` characters, prefixed
    by a hyphen, for use as a flag to the ansible-playbook command. If verbosity is
    zero, return the empty string.
    """
    v_flag = ""
    if verbosity:
        v_flag = f"-{'v'*verbosity}"
    return v_flag


@invoke.task(pre=[install_requirements], default=True)
def ansible_deploy(c, env=None, tag=None, verbosity=1):
    """Deploy K8s application.

    WARNING: if you are running this in CI, make sure to set `--verbosity=0` to prevent
    environment variables from being logged in plain text in the CI console.

    Config:
        env: The target ansible host ("staging", "production", etc ...)
        tag: Image tag to deploy (default: same as default tag for build & push)
        verbosity: integer level of verbosity from 0 to 4 (most verbose)

    Params:
        env: The target ansible host ("staging", "production", etc ...)
        tag: Image tag to deploy (default: same as default tag for build & push)
        verbosity: integer level of verbosity from 0 to 4 (most verbose)

    Usage: inv deploy.deploy --env=<ENVIRONMENT> --tag=<TAG> --verbosity=<VERBOSITY>
    """
    if env is None:
        env = c.config.env
    if tag is None:
        tag = c.config.tag
    playbook = "deploy.yaml" if os.path.exists("deploy/deploy.yaml") else "deploy.yml"
    v_flag = get_verbosity_flag(verbosity)
    with c.cd("deploy/"):
        c.run(f"ansible-playbook {playbook} -l {env} -e k8s_container_image_tag={tag} {v_flag}")


def get_boto_env(profile_name):
    """
    Use an existing AWS_PROFILE to get the other AWS credentials that boto needs.

    This is a temporary workaround for the bug found here:
    https://github.com/caktus/ansible-role-django-k8s/issues/29#issuecomment-665767426

    If the Ansible IAM role ever gets upgraded to use boto3 instead of boto, or if boto
    itself gets upgraded to handle AWS profiles (less likely), then this function can be
    removed.
    """
    import boto3
    session = boto3.Session(profile_name=profile_name)
    credentials = session.get_credentials().get_frozen_credentials()
    return {
        'AWS_ACCESS_KEY_ID': credentials.access_key,
        'AWS_SECRET_ACCESS_KEY': credentials.secret_key,
        'AWS_SECURITY_TOKEN': credentials.token,
        'AWS_SESSION_TOKEN': credentials.token,
    }


@invoke.task
def ansible_playbook(c, name, extra="", verbosity=1, limit=""):
    """Run a specified Ansible playbook.

    Run a specified Ansible playbook, located in the ``deploy/`` directory. Used to run
    a different playbook than the default playbook.

    WARNING: if you are running this in CI, make sure to set `--verbosity=0` to prevent
    environment variables from being logged in plain text in the CI console.

    Params:
        name: The name of the Ansible playbook to run, including the extension
        extra: Additional command line arguments to ansible-playbook
        verbosity: integer level of verbosity from 0 to 4 (most verbose)

    Usage: inv deploy.playbook <PLAYBOOK.YAML> --extra=<EXTRA> --verbosity=<VERBOSITY>

    """
    if c.config.get("aws") and c.config.aws.get("profile_name"):
        # if we're using AWS and using an AWS_PROFILE, then we'll adjust the
        # shell environment for boto's sake
        shell_env = get_boto_env(c.config.aws.get("profile_name"))
    else:
        shell_env = {}
    if limit:
        limit = f"-l{limit}"
    if "env" in c.config and c.config.env and not limit:
        limit = f"-l{c.config.env}"
    v_flag = get_verbosity_flag(verbosity)
    with c.cd("deploy/"):
        c.run(
            f"ansible-playbook {name} {limit} {extra} {v_flag}",
            env=shell_env
        )


deploy = invoke.Collection("deploy")
deploy.add_task(install_requirements, "install")
deploy.add_task(ansible_deploy, "deploy")
deploy.add_task(ansible_playbook, "playbook")
