"""Docker image module.

Provides utilities to build and push Docker images.
"""

import invoke
from colorama import Style


@invoke.task()
def generate_tag(c):
    """
    Generate tag based on local branch & commit hash.
    Set the config "tag" to the resulting tag.

    Usage: inv image.tag
    """
    if not hasattr(c.config, "tag"):
        # gather build context
        branch = c.run("git rev-parse --abbrev-ref HEAD", hide="out").stdout.strip()
        branch = branch.replace("/", "-")  # clean branch name
        commit = c.run("git rev-parse --short HEAD", hide="out").stdout.strip()
        dirty = c.run("git status --short").stdout.strip()
        if dirty:
            dirty = "-dirty"
        c.config.tag = f"{branch}-{commit}{dirty}"
        print(Style.DIM + f"Set config.tag to {c.config.tag}")


@invoke.task(pre=[generate_tag])
def build_image(c, tag=None, dockerfile=None):
    """
    Build Docker image using docker build. Tags with <tag> parameter
    and "latest".

    Params:
        tag: A user supplied tag for the image
        dockerfile: A non-standard Dockerfile location and/or name

    Usage: inv image.build --tag=<TAG> --dockerfile=<PATH_TO_DOCKERFILE>
    """
    if tag is None:
        tag = c.config.tag
    if dockerfile is None:
        dockerfile = "Dockerfile"
    # build app image
    print(Style.DIM + f"Tagging {tag}")
    c.run(f"docker build -t {c.config.app}:latest -t {c.config.app}:{tag} -f {dockerfile} .", echo=True)
    c.config.tag = tag


@invoke.task(pre=[build_image], default=True)
def push_image(c, tag=None):
    """Push Docker image to remote repository.

    push_image is the default task and will, without the tag parameter, generate a
    tag using the git hash and branch name. Then, build and push that image
    to the repository defined for this task.

    Params:
        tag: tag to apply. (Will be generated from git branch/commit
        if not set).

    Usage: inv push --tag=<TAG>
    """
    if tag is None:
        tag = c.config.tag
    print(Style.DIM + f"Pushing {tag} to {c.config.repository}")
    push_tag = f"{c.config.repository}:{tag}"
    c.run(f"docker tag {c.config.app}:{tag} {push_tag}", echo=True)
    c.run(f"docker push {push_tag}", echo=True)


@invoke.task()
def up(c):
    """Brings up deployable image

    Usage: inv image.up
    """
    c.run("docker-compose down")
    c.run("docker-compose run --rm app python manage.py migrate")
    c.run("docker-compose up -d --remove-orphans")


@invoke.task()
def stop(c):
    """Stops deployable image

    Usage: inv image.stop
    """
    c.run("docker-compose stop", warn=True)


image = invoke.Collection("image")
image.add_task(generate_tag, "tag")
image.add_task(build_image, "build")
image.add_task(push_image, "push")
image.add_task(up, "up")
image.add_task(stop, "stop")
