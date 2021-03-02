import invoke
import json
import re
from kubesae.info import print_ansible_vars

ANSIBLE_HEADER = re.compile(r"^.*\s=>\s")
BASE_BACKUP_BUCKET = "caktus-hosting-services-backups"


def result_to_json(result: invoke.Result):
    value = re.sub(ANSIBLE_HEADER, "", result.stdout.strip())
    try:
        return json.loads(value)
    except json.JSONDecodeError as e:
        print(f"Something went wrong. Expected ansible header. Got {result.stdout.strip()[21]}")


@invoke.task(name="get_db_backup")
def get_backup_from_hosting(c, latest="daily", profile="caktus", backup_name=None, list=False):
    """Downloads a backup from the caktus hosting services bucket

    Params:
        c (invoke.Context): the running context
        latest (str, optional): Gets the latest backup from the specified temporal period. 
            Defaults to "daily". Options are "daily", "weekly", "monthly", "yearly"
        profile (str, optional): The AWS profile to allow access to the s3 bucket. DEFAULT: "caktus"
        backup_name(str, optional): A specific backup filename.
        list(bool, optional): If set, will list the contents of the bucket for the projects folder and exit.
    
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
    valid_periods = ['daily', 'weekly', 'monthly', 'yearly']

    if "hosting_services_backup_folder" not in c.config.keys():
        print("A hosting services backup folder has not been defined in tasks.py for this project.")
        print(f"Here are a list of the currently defined backup folders:")
        c.run(
            f"aws s3 ls s3://{BASE_BACKUP_BUCKET}/ --profile {profile}"
        )
        print(f"If the project is not listed it will need to be set up with Hosting services, "
              f"see: https://github.com/caktus/ansible-role-k8s-hosting-services")
        return

    if list:
        c.run(
            f"aws s3 ls s3://{BASE_BACKUP_BUCKET}/{c.config.hosting_services_backup_folder}/ --profile {profile}"
        )
        return

    if latest not in valid_periods:
        print(f"{latest} is not a valid backup interval. Valid intervals are {', '.join(valid_periods)}")
        exit(1)

    if not backup_name:
        listing = c.run(
            f"aws s3 ls s3://{BASE_BACKUP_BUCKET}/{c.config.hosting_services_backup_folder}/ --profile {profile}",
            pty=False,
            hide="out",
        ).stdout.strip()

        dates = [
            re.search(r"\d{12}", x).group(0)
            for x in listing.split("\n")
            if re.search(f"^.*{latest}-.*", x)
        ]

        backup_name = f"{latest}-{c.config.hosting_services_backup_folder}-{dates[-1]}.pgdump"
    
    c.run(
        f"aws s3 cp s3://{BASE_BACKUP_BUCKET}/{c.config.hosting_services_backup_folder}/{backup_name} ./{backup_name} --profile {profile}"
    )


utils = invoke.Collection("utils")
utils.add_task(get_backup_from_hosting)
