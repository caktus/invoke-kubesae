Releases
========


v0.1.1, 2025-07-17
~~~~~~~~~~~~~~~~~~~
* Fix exec into pod command (#52)

v0.1.0, 2022-12-01
~~~~~~~~~~~~~~~~~~~
* Add simpler helper to restore backups (``deploy.db-restore``) when testing disaster recovery tasks (#49)
* Fix ``utils.get-db-dump`` breaking when output includes kubectl warnings (#48)
* Use pre-commit for: black, flake8, isort, prettier (#50)

v0.0.21, 2022-29-08
~~~~~~~~~~~~~~~~~~~
* Adds a utility `util.scale-app` which assists with scaling a namespace's app and celery deployments and celery-beat statefulset.

v0.0.20, 2022-12-08
~~~~~~~~~~~~~~~~~~~
* Adds support for selecting the flavor of debian launched with pod.debian.

v0.0.19, 2022-19-05
~~~~~~~~~~~~~~~~~~~
* Allow restoring a db from a different schema to another without complaints.

v0.0.18, 2021-14-08
~~~~~~~~~~~~~~~~~~~~

* Support multi-stage Dockerfiles and allow setting the target build stage (`--target`)
* Adds a default value (DATABASE_URL) for `db_var` on tasks requiring database variable name.

v0.0.17, 2021-10-04
~~~~~~~~~~~~~~~~~~~~

* Adds a utility `count_backups` that counts available backups in hosting services s3 buckets.
* Adds a utility `list-backup-schedules` to list schedules present in a project's backup bucket.
* Adds a flag to `aws.sync-media` that allows projects with a single bucket but multiple media folders, to sync between those folders.

v0.0.16, 2021-08-05
~~~~~~~~~~~~~~~~~~~~

* Kubesae is now a PyPI package

v0.0.15, 2021-03-24
~~~~~~~~~~~~~~~~~~~~

* Add support for using any source S3 backup bucket with `config.hosting_services_backup_bucket`


v0.0.14, 2021-03-02
~~~~~~~~~~~~~~~~~~~~

* Adds get_backup_from_hosting to allow retrieving backups that are created and stored using caktus-hosting-backups


v0.0.13, 2021-02-22
~~~~~~~~~~~~~~~~~~~~
* Make custom playbooks compatible with boto. This requires that you add a
  ``aws.profile_name`` key in your tasks definition which points to an AWS_PROFILE that
  is an AssumedRole.


v0.0.12, 2021-02-18
~~~~~~~~~~~~~~~~~~~
* Add support for Ansible `--limit` with `deploy.playbook` task
* Fix bug with verbosity flag


v0.0.11, 2021-02-02
~~~~~~~~~~~~~~~~~~~
* Add verbosity flag to all ansible commands, and allow verbosity=0, with a WARNING
  explaining to use that for CI deploys (#27)


v0.0.10, 2021-01-13
~~~~~~~~~~~~~~~~~~~
* Add ``sync-media`` task (#24)
* Add ``info`` package, with tasks to get ansible variables and pod statistics (#23)


v0.0.9, 2020-10-29
~~~~~~~~~~~~~~~~~~
* Add command to run an alternate playbook (#21)


v0.0.8, 2020-09-15
~~~~~~~~~~~~~~~~~~
* Update shell command to use `container_name` (rather than "app")


v0.0.7, 2020-07-20
~~~~~~~~~~~~~~~~~~
* Add support for Google Cloud Platform
* Shell command uses (and requires) container_name config variable


v0.0.6, 2020-07-13
~~~~~~~~~~~~~~~~~~
* Delete old migrations pods with single command
* Add command to delete collectstatic pods
* Add command to fetch an environment variable from container
* Add command to get a database dump
* Add command to restore a database dump
* Updates docstrings


v0.0.5, 2020-06-22
~~~~~~~~~~~~~~~~~~
* Build images with docker, rather than docker-compose


v0.0.4, 2020-06-22
~~~~~~~~~~~~~~~~~~
* Add and improve docstrings
* Package all the packages, including sub-packages
* Support either .yaml or .yml extension


v0.0.3, 2020-04-28
~~~~~~~~~~~~~~~~~~
* Bump in release version


v0.0.2, 2020-04-28
~~~~~~~~~~~~~~~~~~
* Fix package name


v0.0.1, 2020-04-27
~~~~~~~~~~~~~~~~~~
* Initial release
