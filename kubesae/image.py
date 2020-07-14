"""Docker image module.

Provides utilities to build and push Docker images.
"""

import invoke
import subprocess
from colorama import Style


@invoke.task()
def write_docker_env_file(c):
    """
    Write a docker_env_file, based on the c.docker_env_file_template configuration.

    Usage: inv image.write_docker_env_file

    Config:

        docker_env_file_template_path: Path to the template for the docker_env_file,
            which should have variable names, and commands to get their values, like:
            MOST_RECENT_GIT_REVISION=git rev-parse --short HEAD
            GIT_BRANCH=git rev-parse --abbrev-ref HEAD
    """
    # This is the config variable that should define the path to the docker_env_file template.
    docker_env_file_template_var_name = "docker_env_file_template_path"

    if c.config.get(docker_env_file_template_var_name):
        # This is the content that will be written to the docker_env_file at the
        # end of this method.
        docker_env_file_content = ""

        # Open the template file, and loop through its lines, running the command
        # for each line.
        with open(c.config[docker_env_file_template_var_name], "r") as docker_env_file_template:
            for line in docker_env_file_template.read().split("\n"):
                # If the line is truthy (not empty), then split it up into the
                # variable name and the command. Then run the command, and add
                # its result into the docker_env_file_content.
                # For example, if the line is DEALER_REVISION=git rev-parse --short HEAD,
                # then var_name will be DEALER_REVISION, and command will be
                # "git rev-parse --short HEAD".
                if line:
                    # If the line doesn't have an equal sign (for example, a comment),
                    # then just add the line to the docker_env_file_content.
                    if line.count("=") == 0:
                        docker_env_file_content += f"{line}\n"
                    else:
                        var_name = line.split("=")[0]
                        command = line[len(var_name) + 1:]
                        result = subprocess.run(
                            command,
                            capture_output=True,
                            shell=True
                        ).stdout.decode('utf-8').rstrip()
                        docker_env_file_content += f"{var_name}={result}\n"

        # Write the docker_env_file_content into the docker_env_file.
        with open("docker_env_file", "w") as docker_env_file:
            docker_env_file.write(docker_env_file_content)
        print("docker_env_file written")
    else:
        raise KeyError(f"Please set '{docker_env_file_template_var_name}' in config file")


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
        tag: A user supplied tag for the generated image.

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
image.add_task(write_docker_env_file, "write-docker-env-file")
image.add_task(generate_tag, "tag")
image.add_task(build_image, "build")
image.add_task(push_image, "push")
image.add_task(up, "up")
image.add_task(stop, "stop")
