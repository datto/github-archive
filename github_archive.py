#!/usr/bin/env python3

"""
This file is part of github-archive.

Copyright Datto, Inc.

Licensed under the GNU Lesser General Public License Version 3
Fedora-License-Identifier: LGPLv3+
SPDX-2.0-License-Identifier: LGPL-3.0+
SPDX-3.0-License-Identifier: LGPL-3.0-or-later

github-archive is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

github-archive is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with github-archive.  If not, see <https://www.gnu.org/licenses/>.
"""

import configparser
class Config:
    def __init__(self, filename="github_archive.conf"):
        config = configparser.ConfigParser()
        config.read(filename)

        self.gh_db_config = config['GITHUB_ENTERPRISE_DB']
        self.archive_config = config['ARCHIVE']

import MySQLdb
class GithubDatabase:
    def __init__(self, config):
        self.config = config
        self.db = MySQLdb.connect(user='root',
                                  host=config['host'],
                                  passwd=config['password'],
                                  db="github_enterprise")

    def __query_generator(self, query):
        try:
            cursor = self.db.cursor()
            cursor.execute(query)
        except: # The db connection will drop after a long time, so... hacky reconnect
            self.__init__(self.config)
            cursor = self.db.cursor()
            cursor.execute(query)
        while True:
            retval = cursor.fetchone()
            if retval is None:
                break
            yield retval

    def gists(self):
        # repo_name is misleadingly named: It's almost always the sha1 or a sequential ID
        return self.__query_generator("SELECT repo_name, user_id, public FROM gists")

    def repositories(self):
        return self.__query_generator("SELECT id, name, owner_id, public FROM repositories")

    def users(self):
        return self.__query_generator("SELECT id, login FROM users")

import pathlib
import subprocess
class Archive:
    def __init__(self, config):
        self.repos_dir = pathlib.Path(config['gh_repos_local_dir'])
        if not self.repos_dir.is_dir():
            raise FileNotFoundError("Configured gh_repos_local_dir must exist and be a directory.")
        self.archive_dir = pathlib.Path(config['archive_local_dir'])
        # For now we're recreating the archive from scratch every time. Given a folder for a repo
        # exists, I'm not sure how to guarantee that its objects are in a complete state.
        self.archive_dir.mkdir(parents=True)
        # Local repos/gist paths keyed by ID
        # I'm not using ** in the first glob because it excludes gists this way - depth matters
        self.local_repos = {path.stem: path
                            for path in self.repos_dir.glob('*/nw/*/*/*/*/*.git')}
        self.local_gists = {path.stem: path
                            for path in self.repos_dir.glob('**/gist/*.git')}

    def mirror_repo(self, repo_id, repo_name, owner_login, is_public):
        visibility = "public" if is_public else "private"
        repo_archive_dest = self.archive_dir/visibility/owner_login/"repositories"/repo_name
        # Git will make the repo's directory for us.
        repo_archive_dest.parent.mkdir(parents=True, exist_ok=True)
        repo_git_dir = self.local_repos[str(repo_id)]
        result = subprocess.run(['git', 'clone', '--mirror', '--dissociate',
                                 repo_git_dir, repo_archive_dest])

    def clone_gist(self, gist_name, owner_login, is_public):
        visibility = "public" if is_public else "private"
        gist_archive_dest = self.archive_dir/visibility/owner_login/"gists"/gist_name
        gist_archive_dest.parent.mkdir(parents=True, exist_ok=True)
        gist_git_dir = self.local_gists[str(gist_name)]
        # Unlike with repos, I think it's ok to have a working copy because gists are pretty much
        # always small, and won't have branches/tags. Plus, they're poorly named, so this makes
        # the archive more greppable if you need to find one.
        result = subprocess.run(['git', 'clone', gist_git_dir, gist_archive_dest])

def main(db, archive):
    users = {user_id: user_login for user_id, user_login in db.users()}

    for repo_id, repo_name, owner_id, is_public in db.repositories():
        archive.mirror_repo(repo_id, repo_name, users[owner_id], bool(is_public))
    for gist_name, owner_id, is_public, in db.gists():
        archive.clone_gist(gist_name, users[owner_id], bool(is_public))

if __name__ == "__main__":
    cfg = Config()
    main(GithubDatabase(cfg.gh_db_config), Archive(cfg.archive_config))
