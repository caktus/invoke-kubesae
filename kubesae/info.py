import invoke
import yaml

@invoke.task("print_ansible_vars")
def print_ansible_vars(c, var=None, yaml=None, pty=True, hide=False):
    """A command to inspect any ansible varible by environment. If no variable is specified then it will
    print out the current k8s environment variables.

    Args:
        c (invoke.Context): [description]
        var (string, optional): The ansible variable you want to expose. Defaults to None.
        yaml (string, optional): An ansible path. Defaults to None.
        pty (bool, optional): [description]. Defaults to True.
        hide (bool, optional): [description]. Defaults to False.

    Returns:
        invoke.Result
    
    Usage:
        $ inv staging info.print_ansible_vars
            Prints all of the environment variables values defined in the 
            "k8s_environment_variables" dictionary located at 
            <PROJECT_ROOT>/deploy/host_vars/staging.yml.

        $ inv staging info.print_ansible_vars --var=foo_bar_baz
            Prints the "foo_bar_baz" value defined in the "foo_bar_baz"
            variable located at <PROJECT_ROOT>/deploy/host_vars/staging.yml
        
        $ inv staging info.print_ansible_vars --var=foo_bar_baz --yaml="@group_vars/all.yaml"
            Prints the "foo_bar_baz" value defined in the "foo_bar_baz"
            variable located at <PROJECT_ROOT>/deploy/group_vars/all.yml
    """
    yaml_file = f"@host_vars/{c.config.env}.yml"
    expose_var = "k8s_environment_variables"
    if var:
        expose_var = var
    if yaml:
        yaml_file = yaml

    cmd = f"ansible {c.config.env} -m debug -a var='{expose_var}' -e '{yaml_file}'"
    with c.cd("deploy/"):
        return c.run(cmd, pty=pty, hide=hide)


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
info.add_task(print_ansible_vars)
info.add_task(pod_stats)