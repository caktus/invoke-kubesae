import invoke


@invoke.task(default=True)
def shell(c):
    """Gives you a shell on the application pod.

    Usage: inv <ENVIRONMENT> pod
    """
    c.run(f"kubectl exec -it deploy/app -n {c.config.namespace} bash")


@invoke.task()
def clean_debian(c):
    """Clears away the old debian pod so a new one may live.

    Usage: inv pod.clean-debian
    """
    c.run(f"kubectl delete pod debian", warn=True)


@invoke.task(pre=[clean_debian])
def debian(c):
    """An ephemeral container with which to run sysadmin tasks on the cluster

    Usage: inv pod.debian
    """
    c.run(f"kubectl run -it debian --image=debian:bullseye-slim --restart=Never -- bash")


@invoke.task
def clean_collectstatic(c):
    """Removes all collectstatic pods

    Usage: inv pod.clean-collectstatic
    """
    c.run(
        f"kubectl delete pods -n {c.config.namespace} -ljob-name=collectstatic"
    )

@invoke.task
def clean_migrations(c):
    """Removes all migration pods

    Usage: inv pod.clean-migrations
    """
    c.run(
        f"kubectl delete pods -n {c.config.namespace} -ljob-name=migrate"
    )

# TODO: Implement database related tasks
@invoke.task
def get_current_database(c):
    pass


pod = invoke.Collection("pod")
pod.add_task(shell, "shell")
pod.add_task(clean_debian, "clean_debian")
pod.add_task(debian, "debian")
pod.add_task(clean_migrations, "clean_migrations")
