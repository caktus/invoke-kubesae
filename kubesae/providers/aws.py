"""AWS provider module.

Provides helpful EKS and ECR utilities.
"""

import invoke
from colorama import Style


@invoke.task()
def aws_docker_login(c):
    """Obtain ECR credentials to use with docker login.
    
    Usage: inv aws.docker_login
    """
    registry = c.config.repository.split("/")[0]
    print(Style.DIM + f"Performing {registry} registry authentication")
    c.run(
        f"aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin {registry}"
    )


@invoke.task()
def configure_eks_kubeconfig(c, cluster=None, region=None):
    """Obtain EKS access token.
    
    Usage: inv aws.configure_eks_kubconfig --cluster=<CLUSTER> --region=<REGION>
    """
    if not cluster:
        cluster = c.config.cluster
    if not region:
        region = "us-east-1"
    c.run(f"aws eks update-kubeconfig --name {cluster} --region {region}")


aws = invoke.Collection("aws")
aws.add_task(aws_docker_login, "docker_login")
aws.add_task(configure_eks_kubeconfig, "configure_eks_kubeconfig")
