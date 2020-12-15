import invoke
import yaml

@invoke.task(default=True)
def get_ansible_vars(c, var=None):
    """A command to inspect any ansible varible by environment. If no variable is specified then it will
    print out the current k8s environment variables.

    Params:
        var: A variable available to a host when called.

    Usage: inv <ENVIRONMENT> info
           inv <ENVIRONEMNT> info --var=<ANSIBLE_VAR>
    """
    if not var:
        var = "k8s_environment_variables"
    with c.cd("deploy/"):
        c.run(f"ansible {c.config.env} -m debug -a var='{var}' -e '@host_vars/{c.config.env}.yml'")

@invoke.task
def pod_stats(c):
    """Report total pods vs pod capacity in a cluster.
    
    Params: None

    Usage: inv info.pod-stats
    """
    nodes = yaml.safe_load(c.run("kubectl get nodes -o yaml", hide="out").stdout)
    pod_capacity = sum([int(item["status"]["capacity"]["pods"]) for item in nodes["items"]])
    pod_total = c.run(
        "kubectl get pods --all-namespaces | grep Running | wc -l", hide="out"
    ).stdout.strip()
    print(f"Running pods: {pod_total}")
    print(f"Maximum pods: {pod_capacity}")
    print(f"Total nodes: {len(nodes['items'])}")

info = invoke.Collection("info")
info.add_task(get_ansible_vars)
info.add_task(pod_stats)