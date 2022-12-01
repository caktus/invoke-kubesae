import pytest

from kubesae.utils import BASE_BACKUP_BUCKET, get_backup_from_hosting


@pytest.fixture
def test_bucket(c):
    backup_bucket = "test-bucket"
    c.config.hosting_services_backup_bucket = backup_bucket
    return backup_bucket


@pytest.fixture
def test_folder(c):
    backup_folder = "test-project"
    c.config.hosting_services_backup_folder = backup_folder
    return backup_folder


@pytest.fixture
def s3_filename(c, test_folder):
    filename = f"daily-{test_folder}-202101010000.pgdump"
    listing = f"2021-01-01 08:00:00 111266 {filename}"
    c.run.return_value.stdout.strip.return_value = listing
    return filename


def test_backup_bucket__default(c, test_folder):
    get_backup_from_hosting(c, backup_name="-")
    assert f"aws s3 cp s3://{BASE_BACKUP_BUCKET}" in c.run.call_args.args[0]


def test_backup_bucket__custom(c, test_bucket, test_folder):
    get_backup_from_hosting(c, backup_name="-")
    assert f"aws s3 cp s3://{test_bucket}" in c.run.call_args.args[0]


def test_bucket_folder(c, test_bucket, test_folder):
    get_backup_from_hosting(c, backup_name="-")
    cmd = c.run.call_args.args[0]
    assert f"aws s3 cp s3://{test_bucket}/{test_folder}" in cmd


def test_backup_name__default(c, test_bucket, test_folder, s3_filename):
    get_backup_from_hosting(c)
    assert f"./{s3_filename}" in c.run.call_args.args[0]


def test_backup_name__custom(c, test_bucket, test_folder):
    get_backup_from_hosting(c, backup_name="mydb.pgdump")
    assert "./mydb.pgdump" in c.run.call_args.args[0]
