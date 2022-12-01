import json
import re

import invoke

ANSIBLE_HEADER = re.compile(r"^.*\s=>\s")
BASE_BACKUP_BUCKET = "caktus-hosting-services-backups"


def process_backups(schedule_list, search_list):
    result = {}
    for schedule in schedule_list:
        result[schedule] = len(re.findall(f"{schedule}-.*\\.pgdump", search_list))
    return result


def result_to_json(result: invoke.Result):
    value = re.sub(ANSIBLE_HEADER, "", result.stdout.strip())
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        print(
            f"Something went wrong. Expected ansible header. Got {result.stdout.strip()[21]}"
        )


@invoke.task(name="get_db_backup")
def get_backup_from_hosting(
    c, latest="daily", profile="caktus", backup_name=None, list=False, dest=""
):
    """Downloads a backup from the caktus hosting services bucket

    Params:
        c (invoke.Context): the running context
        latest (str, optional): Gets the latest backup from the specified temporal period.
            Defaults to "daily".
        profile (str, optional): The AWS profile to allow access to the s3 bucket. DEFAULT: "caktus"
        backup_name(str, optional): A specific backup filename.
        list(bool, optional): If set, will list the contents of the bucket for the projects folder and exit.
        dest (str, optional): Output filename

    Usage:
        $ inv utils.get-db-backup
            Will copy the latest daily backup to project project root

        $ inv utils.get-db-backup --latest=monthly
            Will copy the latest monthly backup to the project root

        $ inv utils.get-db-backup --backup-name=yearly-2021.pgdump
            Will copy the backup file with the name "yearly-2021.pgdump" to the project root

        $ inv utils.get-db-backup --list
            Will list all of the backup files in the bucket for the project.

        $ inv utils.get-db-backup --list --profile="client-aws"
            Will list all of the backup files using the a locally configured AWS_PROFILE named "client-aws"
    """

    if c.config.get("hosting_services_backup_profile"):
        profile = c.config.hosting_services_backup_profile
    if c.config.get("hosting_services_backup_bucket"):
        bucket = f"s3://{c.config.hosting_services_backup_bucket.strip('/')}"
    else:
        bucket = f"s3://{BASE_BACKUP_BUCKET.strip('/')}"

    if c.config.get("hosting_services_backup_folder"):
        bucket_folder = f"{bucket}/{c.config.hosting_services_backup_folder.strip('/')}"
    else:
        print(
            "A hosting services backup folder has not been defined in tasks.py for this project."
        )
        print("Here are a list of the currently defined backup folders:")
        c.run(f"aws s3 ls {bucket} --profile {profile}")
        print(
            "If the project is not listed it will need to be set up with Hosting services, "
            "see: https://github.com/caktus/ansible-role-k8s-hosting-services"
        )
        return

    if list:
        c.run(f"aws s3 ls {bucket_folder}/ --profile {profile}")
        return

    if not backup_name:
        listing = c.run(
            f"aws s3 ls {bucket_folder}/ --profile {profile}",
            pty=False,
            hide="out",
        ).stdout.strip()

        dates = [
            re.search(r"\d{12}", x).group(0)
            for x in listing.split("\n")
            if re.search(f"^.*{latest}-.*", x)
        ]
        if dates:
            backup_name = (
                f"{latest}-{c.config.hosting_services_backup_folder}-{dates[-1]}.pgdump"
            )

    if not dest:
        dest = backup_name
    if not backup_name:
        print(f"No backup matching a latest of {latest} could be found.")
        return
    c.run(f"aws s3 cp {bucket_folder}/{backup_name} ./{dest} --profile {profile}")


@invoke.task
def list_backup_schedules(
    c, bucket_identifier="caktus-hosting-services-backups", profile="caktus"
):
    """
    Lists the backup schedules found in a project's hosting bucket.
    :param c:
    :param bucket_identifier: The name of the bucket that holds the backups.
    :param profile:
    :return:
    """

    hosting_bucket = (
        c.hosting_services_backup_folder
        if c.config.hosting_services_backup_folder
        else c.config.app
    )
    all_backups = c.run(
        f"aws s3 ls s3://{bucket_identifier}/{hosting_bucket}/ --profile={profile}",
        hide="out",
    ).stdout.strip()

    schedules = []
    print(f"Backup schedules found at {hosting_bucket}\n")
    for backup in all_backups.split("\r\n"):
        name = backup.split(" ")[-1].split("-")[0]
        if name not in schedules:
            schedules.append(name)
            print(f"{name}")


@invoke.task
def count_backups(
    c,
    bucket_identifier="caktus-hosting-services-backups",
    profile="caktus",
    extra_schedules="",
):
    """
    count_backups sorts the backups generated with caktus-hosting-services cronjob and prints the number found of each type.

    :param c: Context
    :param bucket_identifier: The name of the bucket that holds the backups.
    :param profile: The profile with list access to the bucket.
    :param extra_schedules: A string passed in with a comma delimiting each additional schedule name.
    """
    extended = []
    if extra_schedules:
        extended = [x for x in extra_schedules.split(",") if x != ""]

    schedules = ["daily", "weekly", "monthly", "yearly"] + extended
    hosting_bucket = (
        c.hosting_services_backup_folder
        if c.config.hosting_services_backup_folder
        else c.config.app
    )

    all_backups = c.run(
        f"aws s3 ls s3://{bucket_identifier}/{hosting_bucket}/ --profile={profile}",
        hide="out",
    ).stdout.strip()

    sorted_backups = process_backups(schedules, all_backups)

    print("Backups found:\n")
    for k, v in sorted_backups.items():
        print(f"{v:03d}: {k}\n")


@invoke.task
def scale_app(c, down=False, celery=False, container_count=2):
    """A utility to simplify scaling namespace app pods and optionally celery pods.

    Developed primarily to assist with backup verifications. Following the instructions in
    https://caktus.github.io/developer-documentation/reference/backups/

    If the namespace is using a standard django-k8s celery deployment, you can specify --celery in the command to
    scale the celery worker and beat appropriately.

    Usage:
        inv staging utils.scale-app --down  # Scales the containers to 0.
        inv staging utils.scale-app --down --celery  # Scales the containers, celery-worker, and celery-beat to 0.
        inv staging utils.scale-app  # Scales the containers to 2.
        inv staging utils.scale-app --celery  # Scales the containers to 2, and celery-worker/celery-beat to 1.
        inv staging utils.scale-app --container-count 4  # Scales the containers to 4.
        inv staging utils.scale-app --container-count 4 --celery  # Scales the containers to 4, and celery-worker/celery-beat to 1.
    """

    if down:
        print(f"Scaling the deployment {c.config.container_name} DOWN to 0 replicas.")
        c.run(
            f"kubectl scale -n {c.config.namespace} deploy/{c.config.container_name} --replicas=0"
        )
        if celery:
            # celery needs to scale the celery-worker deployment and the celery-beat stateful-set
            print("Scaling celery worker and beat DOWN to 0 replicas")
            c.run(
                f"kubectl scale -n {c.config.namespace} deploy/celery-worker --replicas=0"
            )
            c.run(
                f"kubectl scale -n {c.config.namespace} statefulsets celery-beat --replicas=0"
            )
    else:
        print(
            f"Scaling the deployment {c.config.container_name} UP to {container_count} replicas."
        )
        c.run(
            f"kubectl scale -n {c.config.namespace} deploy/{c.config.container_name} --replicas={container_count}"
        )
        if celery:
            # celery needs to scale the celery-worker deployment and the celery-beat stateful-set
            print("Scaling celery worker and beat to 1 replica.")
            c.run(
                f"kubectl scale -n {c.config.namespace} deploy/celery-worker --replicas=1"
            )
            c.run(
                f"kubectl scale -n {c.config.namespace} statefulsets celery-beat --replicas=1"
            )


utils = invoke.Collection("utils")
utils.add_task(get_backup_from_hosting)
utils.add_task(count_backups)
utils.add_task(list_backup_schedules)
utils.add_task(scale_app)
