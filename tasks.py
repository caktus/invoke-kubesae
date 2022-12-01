import invoke

from colorama import init

from kubesae import aws, deploy, image, info, pod

init(autoreset=True)


@invoke.task
def staging(c):
    c.config.env = "staging"
    c.config.namespace = "myproject-staging"
    c.config.container_name = "myproject-web"


ns = invoke.Collection()
ns.add_collection(image)
ns.add_collection(aws)
ns.add_collection(deploy)
ns.add_collection(pod)
ns.add_collection(info)
ns.add_task(staging)

ns.configure(
    {
        "app": "myproject",
        "aws": {
            "region": "us-west-2",
            "profile_name": "my-aws-profile",  # a profile from .aws/credentials
        },
        "cluster": "Myproject-EKS-cluster",
        "repository": "123456789012.dkr.ecr.us-east-1.amazonaws.com/myproject",
        "hosting_services_backup_folder": "myproject",
        "run": {
            "echo": True,
            "pty": True,
        },
    }
)
