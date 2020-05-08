import invoke
from colorama import init
from kubesae import *


init(autoreset=True)


@invoke.task
def staging(c):
    c.config.env = "staging"


ns = invoke.Collection()
ns.add_collection(image)
ns.add_collection(aws)
ns.add_collection(deploy)
ns.add_collection(pod)
ns.add_task(staging)
ns.configure({"run": {"echo": True}})
