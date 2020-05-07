"""AWS provider module.

Provides helpful EKS and ECR utilities.
"""

import invoke
from colorama import Style


@invoke.task()
def aws_docker_login(c):
    """
    Obtain ECR credentials to use with docker login.

    Config:

        aws.region: Name of AWS region (default: us-east-1)
        repository: Name of docker repository, e.g. dockerhub.com/pressweb.
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

    Config:

        aws.region: Name of AWS region (default: us-east-1)
        cluster: Name of EKS cluster
    """
    if not cluster:
        cluster = c.config.cluster
    if not region:
        region = c.config.aws.get("region", "us-east-1")
    c.run(f"aws eks update-kubeconfig --name {cluster} --region {region}")


aws = invoke.Collection("aws")
aws.add_task(aws_docker_login, "docker-login")
aws.add_task(configure_eks_kubeconfig, "configure-eks-kubeconfig")
