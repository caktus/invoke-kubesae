"""GCP provider module.

Provides helpful utilities for working with kubernetes and the Google Container Registry.
"""

import invoke
from colorama import Style


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


gcp = invoke.Collection("gcp")
gcp.add_task(gcp_docker_login, "docker-login")
gcp.add_task(configure_gcp_kubeconfig, "configure-gcp-kubeconfig")
