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
def get_backup_from_hosting(c, latest="daily", backup_name=None, list=False):
    """Downloads a backup from the caktus hosting services bucket

    Args:
        c (invoke.Context): the running context
        latest (str, optional): Gets the latest backup from the specified temporal period. 
            Defaults to "daily". Options are "daily", "weekly", "monthly", "yearly"
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
    """
    c.config.env = "production"
    VALID_PERIODS = ['daily', 'monthly', 'yearly']

    project_backup_folder = print_ansible_vars(
            c,
            var="k8s_hosting_services_project_name",
            yaml="@group_vars/cluster.yaml",
            pty=False,
            hide=True,
    )

    project_backup_folder = result_to_json(project_backup_folder)["k8s_hosting_services_project_name"]
    
    if list:
        c.run(
            f"aws s3 ls s3://{BASE_BACKUP_BUCKET}/{project_backup_folder}/ --profile caktus"
        )
        return

    if latest in VALID_PERIODS and not backup_name:

        listing = c.run(
            f"aws s3 ls s3://{BASE_BACKUP_BUCKET}/{project_backup_folder}/ --profile caktus",
            pty=False,
            hide=True,
        ).stdout.strip()

        dates = [
            re.search("\d{12}", x).group(0)
            for x in listing.split("\n")
            if re.search(f"^.*{latest}-.*", x)
        ]

        backup_name = f"{latest}-{project_backup_folder}-{dates[-1]}.pgdump"
    
    c.run(
        f"aws s3 cp s3://{BASE_BACKUP_BUCKET}/{project_backup_folder}/{backup_name} ./{backup_name} --profile caktus"
    )

utils = invoke.Collection("utils")
utils.add_task(get_backup_from_hosting)
