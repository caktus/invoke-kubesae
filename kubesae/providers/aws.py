"""AWS provider module.

Provides helpful EKS and ECR utilities.
"""
import re
import invoke
from colorama import Style
from kubesae.pod import fetch_namespace_var


@invoke.task()
def aws_docker_login(c):
    """
    Obtain ECR credentials to use with docker login.

    Usage: inv aws.docker_login

    Config:

        aws.region: Name of AWS region (default: us-east-1)
        repository: Name of docker repository, e.g. dockerhub.com/myproject.
    """
    registry = c.config.repository.split("/")[0]
    region = c.config.aws.get("region", "us-east-1")
    print(Style.DIM + f"Performing {registry} registry authentication")
    c.run(
        f"aws ecr get-login-password --region {region} | docker login --username AWS --password-stdin {registry}"
    )


@invoke.task()
def configure_eks_kubeconfig(c, cluster=None, region=None):
    """
    Obtain EKS access token.

    Usage: inv aws.configure_eks_kubconfig --cluster=<CLUSTER> --region=<REGION>

    Config:

        aws.region: Name of AWS region (default: us-east-1)
        cluster: Name of EKS cluster
    """
    if not cluster:
        cluster = c.config.cluster
    if not region:
        region = c.config.aws.get("region", "us-east-1")
    c.run(f"aws eks update-kubeconfig --name {cluster} --region {region}")


@invoke.task(name="sync_media")
def sync_media_tree(
    c,
    sync_to="staging",
    media_bucket="MEDIA_STORAGE_BUCKET_NAME",
    acl="private",
    local_target="./media",
    bucket_path="",
    sibling=False,
    dry_run=False,
    delete=False,
):
    """Syncs a media bucket between two namespaces (e.g. `production` to `staging`, or `staging` to `local`).

    Params:
        sync_to      (string, required): A deployment host defined in ansible host_vars (e.g. "production", "staging", "dev"), or "local".
            If set to "local" the tree will sync to a local folder. DEFAULT: staging.
        media_bucket (string, required): The variable name for media defined in settings and host_vars. DEFAULT: MEDIA_STORAGE_BUCKET_NAME
        acl          (string, required): Sets the access policy on each object. DEFAULT: private
                                         Possible values: [
                                            private, public-read, public-read-write, authenticated-read,
                                            aws-exec-read, bucket-owner-read,bucket-owner-full-control,
                                            log-delivery-write
                                        ]
        local_target (string, optional): Sets a target directory for local syncs. Defaults to "./media"
        dry_run      (boolean, optional): Outputs the result to stdout without applying the action
        bucket_path (string, optional): If set, appends to the bucket the extra path information.
        sibling     (boolean, optional): If set, assumes that the target bucket is on the same S3 bucket but in a different location folder. Uses the `sync_to` for target path.
        delete       (boolean, optional): If set, deletes files on the target that do not exist on the source.

    Usage:
        inv production aws.sync-media --dry-run:
            Will simulate a sync from production to staging using the s3 bucket defined in MEDIA_STORAGE_BUCKET with no acl applied.

        inv production aws.sync-media --dry-run --delete
            Will display the files that will be deleted from the staging s3 bucket defined in MEDIA_STORAGE_BUCKET.

        inv production aws.sync-media --media-bucket="MEDIA" --acl public-read --delete
            Will sync files from the s3 bucket defined in the environment variable "MEDIA" to a staging bucket with the acl of each object set to 'public-read', and
            will delete objects on the staging bucket that do not exist on the production bucket.

        inv production aws.sync-media --sync-to="local" --local-target="./public/media"
            Will sync files from the production bucket to "<PROJECT_ROOT>/public/media"

        inv production aws.sync-media --sync-to="local" --local-target="./public/media/chandler-bing" --bucket-path="chandler-bing"
    """
    sync_from = c.config.env
    target_media_name = ""
    dr = ""
    dl = ""
    sibling_bucket = ""

    source_media_name = fetch_namespace_var(
        c, fetch_var=f"{media_bucket}"
    ).stdout.strip()

    if bucket_path:
        source_media_name += f"/{bucket_path.strip('/')}"

    if sync_from == sync_to:
        print("Source and Target environments are the same. Nothing to be done.")
        return

    if sync_to == "local":
        target_media_name = local_target
    else:
        cc = invoke.context.Context()
        cc.config.env = sync_to
        cc.config.namespace = f"{c.config.app}-{sync_to}"
        cc.config.container_name = c.config.container_name

        if sibling:
            cc.config.env = c.config.env
            cc.config.namespace = c.config.namespace
            sibling_bucket = f"/{sync_to}"

        target_media_name = fetch_namespace_var(
            cc, fetch_var=f"{media_bucket}"
        ).stdout.strip()
        target_media_name = f"s3://{target_media_name}{sibling_bucket}"

    if dry_run:
        dr = "--dryrun"
    if delete:
        dl = "--delete"

    c.run(f"aws s3 sync --acl {acl} s3://{source_media_name} {target_media_name} {dr} {dl}")


aws = invoke.Collection("aws")
aws.add_task(aws_docker_login, "docker-login")
aws.add_task(configure_eks_kubeconfig, "configure-eks-kubeconfig")
aws.add_task(sync_media_tree, "sync_media")
