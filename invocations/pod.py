import invoke


@invoke.task(default=True)
def shell(c):
    """Gives you a shell on the application pod."""
    c.run(f"kubectl exec -it deploy/app -n {c.config.namespace} bash")


@invoke.task()
def clean_debian(c):
    """Clears away the old pod so a new one may live."""
    c.run(f"kubectl delete pod debian", warn=True)


@invoke.task(pre=[clean_debian])
def debian(c):
    """An ephemeral container with which to run sysadmin tasks on the cluster"""
    c.run(f"kubectl run -it debian --image=debian:bullseye-slim --restart=Never -- bash")


@invoke.task
def clean_migrations(c):
    """Removes all migration jobs"""
    c.run(
        f"kubectl get pod -n {c.config.namespace} -ljob-name=migrate -o name | xargs kubectl delete -n {c.config.namespace}"
    )

@invoke.task
def get_current_database(c):
    pass


pod = invoke.Collection("pod")
pod.add_task(shell, "shell")
pod.add_task(clean_debian, "clean_debian")
pod.add_task(debian, "debian")
pod.add_task(clean_migrations, "clean_migrations")
