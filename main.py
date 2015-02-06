import os
import sys
import json
import random
import shutil
import subprocess
import shlex
import ntplib
from time import ctime
from datetime import datetime, date, timedelta


def clone_repositories(source_repo, target_repo):
    source_name = os.path.splitext(os.path.basename(source_repo))[0]
    target_name = os.path.splitext(os.path.basename(target_repo))[0]

    try:
        os.chdir('/tmp/')
        subprocess.check_output(["git", "clone", source_repo]).decode('ascii')
        subprocess.check_output(["git", "clone", target_repo]).decode('ascii')

        subprocess.check_output(["rm", "-rf", os.path.join("/tmp/{}".format(source_name), '.git')]).decode('ascii')
        subprocess.check_output(["mv", "-f", os.path.join("/tmp/{}".format(source_name), '.gitignore'), "/tmp/{}".format(target_name)]).decode('ascii')
    except Exception as e:
        print("already exists: {}".format(e))
        pass

    return source_name, target_name

def get_source_files(source_name):
    files = []
    # r=root, d=directories, f = files
    for r, d, f in os.walk("/tmp/{}".format(source_name)):
        for file in f:
            files.append(os.path.join(r, file))

    return files


def random_commit(source_name, target_name, commit_date, source_files, max_commit_count):
    total_file_count = len(source_files)
    commit_count = random.randint(1, max_commit_count)
    for commit_index in range(0, commit_count):
        print("commit number: {}".format(commit_index))
        file_no = random.randint(0, total_file_count-1)

        source_file = source_files[file_no]
        target_file = source_file.replace("/tmp/{}".format(source_name), "/tmp/{}".format(target_name))

        if os.path.isfile(target_file):
            os.remove(target_file)
            commit_description = '{} updated'.format(os.path.basename(target_file))
        else:
            os.makedirs(os.path.dirname(target_file), exist_ok=True)
            shutil.copy(source_file, target_file)
            commit_description = '{} added'.format(os.path.basename(target_file))

        os.chdir("/tmp/{}".format(target_name))
        subprocess.check_output(["git", "add", "."]).decode('ascii')

        subprocess.call(shlex.split("timedatectl set-ntp false"))  # May be necessary

        commit_hour = random.randint(9, 18)
        commit_minute = random.randint(0, 59)
        commit_second = random.randint(0, 59)
        commit_time = "{} {}:{}:{}".format(commit_date, commit_hour, commit_minute, commit_second)

        subprocess.call(shlex.split("date -s '{}'".format(commit_time)))
        subprocess.call(shlex.split("hwclock -w"))
        subprocess.check_output(["git", "commit", "-m", commit_description]).decode('ascii')


def scan_date_range(source_name, target_name, start_date, end_date, source_files, everyday=True, exclude=[]):

    start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    while start_date <= end_date:
        if start_date.weekday() not in exclude:
            commit_date = start_date.strftime("%Y-%m-%d")
            print(commit_date)
            random_commit(source_name, target_name, commit_date, source_files, max_commit)

        delta = 1 if everyday else random.randint(1, 2)
        start_date += timedelta(days=delta)


def remove_local_repositories(source_name, target_name):
    subprocess.call(["rm", "-rf", "/tmp/{}".format(source_name)])
    subprocess.call(["rm", "-rf", "/tmp/{}".format(target_name)])


if __name__ == "__main__":

    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config_path) as json_file:
        config = json.load(json_file)

    email = config['email']
    source_repo = config['source_repo'].replace('https://', 'https://{}@'.format(config['access_token']))
    target_repo = config['target_repo'].replace('https://', 'https://{}@'.format(config['access_token']))

    start_date = config['start_date']                   # the start date of commit
    end_date = config['end_date']                       # the last date of commit
    exclude_days = config['exclude_days']               # exclude days from commit, Monday = 0, Sunday = 6
    max_commit = config['max_commit']                   # max commit count per day
    everyday = config['everyday']                       # commit everyday/once in 2 days


    subprocess.call(["git", "config", "--global", "user.email", email])

    try:
        # clone both source/target repositories
        source_name, target_name = clone_repositories(source_repo, target_repo)

        source_files = get_source_files(source_name)

        # commit repository scanning date range
        scan_date_range(
            source_name=source_name,
            target_name=target_name,
            start_date=start_date,
            end_date=end_date,
            source_files=source_files,
            everyday=everyday,
            exclude=exclude_days
        )

        # sync os time with utc time
        ntp_client = ntplib.NTPClient()
        response = ntp_client.request('pool.ntp.org')
        subprocess.call(shlex.split("timedatectl set-ntp false"))  # May be necessary
        utc_time = datetime.strptime(ctime(response.tx_time), "%a %b %d %H:%M:%S %Y")
        subprocess.call(shlex.split("date -s '{}'".format(utc_time)))
        subprocess.call(shlex.split("hwclock -w"))

        # final push to github
        os.chdir("/tmp/{}".format(target_name))
        subprocess.check_output(["git", "push"]).decode('ascii')

        os.chdir("/tmp/")
        remove_local_repositories(source_name, target_name)
        subprocess.call(["git", "config", "--global", "--unset", "user.email"])
    except Exception as e:
        print(e)

        subprocess.call(["git", "config", "--global", "--unset", "user.email"])

        # sync os time with utc time
        ntp_client = ntplib.NTPClient()
        response = ntp_client.request('pool.ntp.org')
        subprocess.call(shlex.split("timedatectl set-ntp false"))  # May be necessary
        utc_time = datetime.strptime(ctime(response.tx_time), "%a %b %d %H:%M:%S %Y")
        subprocess.call(shlex.split("date -s '{}'".format(utc_time)))
        subprocess.call(shlex.split("hwclock -w"))






