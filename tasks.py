import invoke
from colorama import init
from kubesae import image, aws, deploy, pod


init(autoreset=True)


@invoke.task
def staging(c):
    c.config.env = "staging"
    c.config.namespace = "pressweb-staging"
    c.config.container_name = "pressweb-web"


ns = invoke.Collection()
ns.add_collection(image)
ns.add_collection(aws)
ns.add_collection(deploy)
ns.add_collection(pod)
ns.add_task(staging)

ns.configure(
    {
        "app": "pressweb",
        "aws": {
            "region": "us-west-2",
        },
        "cluster": "Pressweb-EKS-cluster",
        "repository": "354308461188.dkr.ecr.us-west-2.amazonaws.com/pressweb",
        "run": {
            "echo": True,
        }
    }
)
