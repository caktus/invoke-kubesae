import invoke


@invoke.task(default=True)
def shell(c):
    """Gives you a shell on the application pod.

    Usage: inv <ENVIRONMENT> pod.shell
    """
    c.run(f"kubectl exec -it deploy/{c.config.container_name} -n {c.config.namespace} bash")


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

    Usage: inv <ENVIRONMENT> pod.clean-migrations
    """
    c.run(
        f"kubectl delete pods -n {c.config.namespace} -ljob-name=migrate"
    )

@invoke.task
def fetch_namespace_var(c, fetch_var, hide=False):
    """Takes a variable name that may be present on a running container. Queries the
    container for the value of that variable and returns it as a Result object.

    Args:
        fetch_var (str): An environment variable expected on the target container
        hide (bool, optional): Hides the stdout if True. Defaults to False.
    Returns:
        [Result]: Invoke Result object.
    Usage:
        inv <ENVIRONMENT> pod.fetch-namespace-var --fetch-var="<VARIABLE_NAME>"
    """
    command = (
        f"kubectl --namespace {c.config.namespace} exec -i "
        f"deploy/{c.config.container_name} -- printenv {fetch_var}"
    )
    return c.run(command, hide=hide)

@invoke.task()
def get_db_dump(c, db_var, filename=None):
    """Get a database dump (into the filename).

    Args:
        db_var (str): The variable name that the database connection is stored in.
        filename (string, optional): A filename to store the dump. Defaults to None.
    Usage:
        inv <ENVIRONMENT> pod.get-db-dump --db-var="<DB_VAR_NAME>"
    """
    database_url = fetch_namespace_var(c, fetch_var=db_var, hide=True).stdout.strip()
    if not filename:
        filename = f"{c.config.namespace}_database.dump"
    command = (
        f"kubectl --namespace {c.config.namespace} exec -i "
        f"deploy/{c.config.container_name} -- pg_dump -Fc --no-owner --clean "
        f"--dbname {database_url} > {filename}"
    )
    c.run(command)

@invoke.task()
def restore_db_from_dump(c, db_var, filename):
    """Load a database dump from a file.

    Args:
        db_var (str): The variable the database connection is stored in.
        filename (string): An filename of the dump to restore.
    Usage:
        inv <ENVIRONMENT> pod.restore-db-from-dump --db-var="<DB_VAR_NAME>" --filename="<PATH/TO/DBFILE>"
    """
    database_url = fetch_namespace_var(c, fetch_var=db_var, hide=True).stdout.strip()
    command = (
        f"kubectl --namespace {c.config.namespace} exec -i "
        f"deploy/{c.config.container_name} -- "
        f"pg_restore --no-owner --clean --if-exists --dbname {database_url} < {filename}"
    )
    c.run(command)

@invoke.task
def sync_media_tree(
    c,
    target_env="staging",
    media_bucket="MEDIA_STORAGE_BUCKET_NAME",
    acl="public-read",
    dry_run=False,
    delete=False,
):
    """Sync an S3 media tree for a given environment to another. 

    Args:
        target_env   (string, required): A deployment host defined in ansible host_vars (e.g. "production", "staging", "dev"). DEFAULT: staging
        media_bucket (string, required): The variable name for media defined in settings and host_vars. DEFAULT: MEDIA_STORAGE_BUCKET_NAME
        acl          (string, required): Sets the access policy on each object. DEFAULT: public-read
                                         Possible values: [
                                            private, public-read, public-read-write, authenticated-read, 
                                            aws-exec-read, bucket-owner-read,bucket-owner-full-control,
                                            log-delivery-write
                                        ]
        dry_run      (boolean, optional): Outputs the result to stdout without applying the action
        delete       (boolean, optional): If set, deletes files on the target that do not exist on the source.

    Usage:
        inv production sync-media --dry-run: 
            Will simulate a sync from production to staging using the s3 bucket defined in MEDIA_STORAGE_BUCKET with no acl applied.
        
        inv production sync-media --dry-run --delete
            Will display the files that will be deleted from the staging s3 bucket defined in MEDIA_STORAGE_BUCKET.
        
        inv production sync-media --media-bucket="MEDIA" --acl public-read --delete
            Will sync files from the s3 bucket defined in the environment variable "MEDIA" to a staging bucket with the acl of each object set to 'public-read', and
            will delete objects on the staging bucket that do not exist on the production bucket.
    """

    cc = invoke.context.Context()
    cc.config.env = target_env
    cc.config.namespace = f"{c.config.app}-{target_env}"
    cc.config.container_name = c.config.container_name

    source_media_name = fetch_namespace_var(
        c, fetch_var=f"{media_bucket}"
    ).stdout.strip()
    target_media_name = fetch_namespace_var(
        cc, fetch_var=f"{media_bucket}"
    ).stdout.strip()

    dr = ""
    dl = ""
    if dry_run:
        dr = "--dryrun"
    if delete:
        dl = "--delete"
    c.run(f"aws s3 sync --acl {acl} s3://{source_media_name} s3://{target_media_name} {dr} {dl}")


pod = invoke.Collection("pod")
pod.add_task(shell, "shell")
pod.add_task(clean_debian, "clean_debian")
pod.add_task(debian, "debian")
pod.add_task(clean_collectstatic, "clean_collectstatic")
pod.add_task(clean_migrations, "clean_migrations")
pod.add_task(get_db_dump, "get_db_dump")
pod.add_task(restore_db_from_dump, "restore_db_from_dump")
pod.add_task(fetch_namespace_var, "fetch_namespace_var")
pod.add_task(sync_media_tree, "sync_media")
