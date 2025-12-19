# Only install PyMySQL as MySQLdb if the native `mysqlclient` (MySQLdb)
# is not available. Django 5+ requires a mysqlclient >= 1.4.3; if
# `mysqlclient` is installed we prefer it. This preserves compatibility
# while allowing PyMySQL to be used in environments without the native
# driver.
import importlib

import pymysql

try:
    # try to import the native MySQLdb module (provided by mysqlclient)
    importlib.import_module("MySQLdb")
except Exception:
    # fall back to PyMySQL if native client isn't present
    pymysql.install_as_MySQLdb()
