"""Docker image module.

Provides utilities to build and push Docker images.
"""

import invoke
from colorama import Style


@invoke.task()
def generate_tag(c):
    """Generate tag based on local branch & commit hash."""
    if not hasattr(c.config, "tag"):
        # gather build context
        branch = c.run("git rev-parse --abbrev-ref HEAD", hide="out").stdout.strip()
        branch = branch.replace("/", "-")  # clean branch name
        commit = c.run("git rev-parse --short HEAD", hide="out").stdout.strip()
        c.config.tag = f"{branch}-{commit}"
        print(Style.DIM + f"Set config.tag to {c.config.tag}")


@invoke.task(pre=[generate_tag])
def build_image(c, tag=None):
    """Build Docker image using docker-compose."""
    if tag is None:
        tag = c.config.tag
    # build app container
    c.run("docker-compose build app", echo=True)
    print(Style.DIM + f"Tagging {tag}")
    c.run(f"docker tag {c.config.app}:latest {c.config.app}:{tag}", echo=True)
    c.config.tag = tag


@invoke.task(pre=[build_image], default=True)
def push_image(c, tag=None):
    """Push Docker image to remote repository."""
    if tag is None:
        tag = c.config.tag
    print(Style.DIM + f"Pushing {tag} to {c.config.repository}")
    push_tag = f"{c.config.repository}:{tag}"
    c.run(f"docker tag {c.config.app}:{tag} {push_tag}", echo=True)
    c.run(f"docker push {push_tag}", echo=True)


@invoke.task()
def up(c):
    """Brings up deployable image"""
    c.run("docker-compose down")
    c.run("docker-compose run --rm app python manage.py migrate")
    c.run("docker-compose up -d --remove-orphans")


@invoke.task()
def stop(c):
    """Stops deployable image"""
    c.run("docker-compose stop", warn=True)


image = invoke.Collection("image")
image.add_task(generate_tag, "tag")
image.add_task(build_image, "build")
image.add_task(push_image, "push")
image.add_task(up, "up")
image.add_task(stop, "stop")
