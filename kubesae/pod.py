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
def clean_migrations(c):
    """Removes all migration jobs

    Usage: inv pod.clean-migrations
    """
    c.run(
        f"kubectl delete pods -n {c.config.namespace} -ljob-name=migrate"
    )

# TODO: Implement database related tasks
@invoke.task
def get_current_database(c):
    pass


@invoke.task()
def get_db_name(c, hide=False):
    command = (
        f"kubectl --namespace {c.config.namespace} exec -i "
        f"deploy/{c.config.container_name} -- printenv DATABASE_URL"
    )
    return c.run(command, hide=hide)


@invoke.task()
def get_db_dump(c, filename=None):
    """Get a database dump (into the filename)."""
    if not filename:
        filename = f"{c.config.namespace}_database.dump"
    database_url = get_db_name(c, hide=True).stdout.strip()
    command = (
        f"kubectl --namespace {c.config.namespace} exec -i "
        f"deploy/{c.config.container_name} -- pg_dump -Fc --no-owner --clean "
        f"--dbname {database_url} > {filename}"
    )
    c.run(command)


@invoke.task()
def load_db_dump(c, filename):
    """Load a database dump from a file."""
    database_url = get_db_name(c, hide=True).stdout.strip()
    command = (
        f"kubectl --namespace {c.config.namespace} exec -i "
        f"deploy/{c.config.container_name} -- "
        f"pg_restore --no-owner --clean --if-exists --dbname {database_url} < {filename}"
    )
    c.run(command)


pod = invoke.Collection("pod")
pod.add_task(shell, "shell")
pod.add_task(clean_debian, "clean_debian")
pod.add_task(debian, "debian")
pod.add_task(clean_migrations, "clean_migrations")
pod.add_task(get_db_name, "get_db_name")
pod.add_task(get_db_dump, "get_db_dump")
pod.add_task(load_db_dump, "load_db_dump")
