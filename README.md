# Creating the archive from a Github Enterprise backup

## Requirements

* A local Github Enterprise backup
    * This was developed against a backup from Github 2.7
* A local MySQL/MariaDB database
* Python 3.6

## Setup

1. Install [mysqlclient-python](https://github.com/PyMySQL/mysqlclient-python) from your source of
   choice. (PyPI, your distro's repositories, source, whatever)  
   **Fedora:**
   ```
   dnf install python3-mysql
   ```
   **PyPI:**
   ```
   pip install mysqlclient
   ```

1. Set up MySQL/MariaDB:
    1. Install and start a MySQL/MariaDB server, however you want.
    2. Unzip `mysql.sql.gz` and insert the contents of `db_setup.sql` at the
       beginning of the resulting `mysql.sql` file.
    3. Load `mysql.sql` into the database

1. Copy `github_archive.conf.dist` to `github_archive.conf` and update the config.

## Running
Run the `github_archive.py` script with no arguments:
```
./github_archive.py
```

# License

This file is part of github-archive.

Copyright Datto, Inc.

Licensed under the GNU Lesser General Public License Version 3

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
