"""GCP provider module.

Provides helpful utilities for working with kubernetes and the Google Container Registry.
"""

import invoke
from colorama import Style
from kubesae.pod import fetch_namespace_var


@invoke.task()
def gcp_docker_login(c):
    """
    Authenticate into GCP, and configure Docker.

    Usage: inv gcp.docker-login

    Config:

        app: Name of the project in GCP
        repository: Name of docker repository, e.g. us.gcr.io/myproject/myproject
    """
    registry = c.config.repository.split("/")[0]
    c.run("gcloud auth login")
    c.run(f"gcloud config set project {c.config.app}")
    c.run(f"gcloud auth configure-docker {registry}")


@invoke.task()
def configure_gcp_kubeconfig(c, cluster=None, region=None):
    """
    Authenticate into GCP to get credentials for the cluster.

    Usage: inv gcp.configure-gcp-kubeconfig --cluster=<CLUSTER> --region=<REGION>

    Config:

        app: Name of the project in GCP
        gcp.region: Name of GCP region (default: us-east1)
        cluster: Name of cluster in GCP (default config.cluster)
    """
    if not cluster:
        cluster = c.config.cluster
    if not region:
        region = c.config.gcp.get("region", "us-east1")
    c.run("gcloud auth login")
    c.run(f"gcloud config set project {c.config.app}")
    c.run(f"gcloud container clusters get-credentials --region={region} {cluster}")

@invoke.task(name="sync_media")
def sync_media_tree(
    c,
    target_env="staging",
    media_bucket="MEDIA_STORAGE_BUCKET_NAME",
    local_target=None,
    dry_run=False,
    delete=False,
):
    """Sync a gcloud media tree for a given environment/namespace to another. 

    Args:
        target_env   (string, required): A deployment host defined in ansible host_vars (e.g. "production", "staging", "dev"). DEFAULT: staging
        media_bucket (string, required): The variable name for media defined in settings and host_vars. DEFAULT: MEDIA_STORAGE_BUCKET_NAME
        local_target (string, optional): Sets a target directory for local syncs
        dry_run      (boolean, optional): Outputs the result to stdout without applying the action
        delete       (boolean, optional): If set, deletes files on the target that do not exist on the source.

    Usage:
        inv production gcp.sync-media --dry-run: 
            Will simulate a sync from production to staging using the bucket defined in MEDIA_STORAGE_BUCKET.
        
        inv production gcp.sync-media --dry-run --delete
            Will display the files that will be deleted from the staging bucket defined in MEDIA_STORAGE_BUCKET.
        
        inv production gcp.sync-media --media-bucket="MEDIA" --delete
            Will sync files from the bucket defined in the environment variable "MEDIA" to a staging bucket and
            will delete objects on the staging bucket that do not exist on the production bucket.
        
        inv production gcp.sync-media --local-target="./media"
            Will sync files from the production s3 bucket to "<PROJECT_ROOT>/media"

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
        dr = "-n"
    if delete:
        dl = "-d"

    target_media_name = f"gs://{target_media_name}"
    if local_target:
        target_media_name = local_target
    c.run(f"gsutil rsync -r {dr} {dl} gs://{source_media_name} {target_media_name}")


gcp = invoke.Collection("gcp")
gcp.add_task(gcp_docker_login, "docker-login")
gcp.add_task(configure_gcp_kubeconfig, "configure-gcp-kubeconfig")
gcp.add_task(sync_media_tree)
