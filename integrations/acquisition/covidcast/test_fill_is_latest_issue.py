"""Integration tests for covidcast's direction updating."""

# standard library
import unittest

# third party
import mysql.connector

# first party
from delphi.epidata.client.delphi_epidata import Epidata
import delphi.operations.secrets as secrets

# py3tester coverage target (equivalent to `import *`)
__test_target__ = 'delphi.epidata.acquisition.covidcast.fill_is_latest_issue'


class FillIsLatestIssueTests(unittest.TestCase):
  """Tests filling is_latest_issue column"""

  def setUp(self):
    """Perform per-test setup."""

    # connect to the `epidata` database and clear the `covidcast` table
    cnx = mysql.connector.connect(
        user='user',
        password='pass',
        host='delphi_database_epidata',
        database='epidata')
    cur = cnx.cursor()
    cur.execute('truncate table covidcast')
    cnx.commit()
    cur.close()

    # make connection and cursor available to test cases
    self.cnx = cnx
    self.cur = cnx.cursor()

    # use the local instance of the epidata database
    secrets.db.host = 'delphi_database_epidata'
    secrets.db.epi = ('user', 'pass')

    # use the local instance of the Epidata API
    Epidata.BASE_URL = 'http://delphi_web_epidata/epidata/api.php'

  def tearDown(self):
    """Perform per-test teardown."""
    self.cur.close()
    self.cnx.close()

  def test_fill_is_latest_issue(self):
    """Update rows having a stale `direction` field and serve the results."""

    self.cur.execute('''
      insert into covidcast values
        (0, 'src', 'sig', 'day', 'state', 20200228, 'ca',
          123, 2, 5, 5, 5, NULL, 20200228, 0, 1, False),
        (0, 'src', 'sig', 'day', 'state', 20200228, 'ca',
          123, 2, 0, 0, 0, NULL, 20200229, 1, 1, False),
        (0, 'src', 'sig', 'day', 'state', 20200229, 'ca',
          123, 6, 0, 0, 0, NULL, 20200301, 1, 1, False),
        (0, 'src', 'sig', 'day', 'state', 20200229, 'ca',
          123, 6, 9, 9, 9, NULL, 20200229, 0, 1, False),
        (0, 'src', 'sig', 'day', 'state', 20200301, 'ca',
          123, 5, 0, 0, 0, NULL, 20200303, 2, 1, False),
        (0, 'src', 'sig', 'day', 'state', 20200301, 'ca',
          123, 5, 5, 5, 5, NULL, 20200302, 1, 1, False),
        (0, 'src', 'sig', 'day', 'state', 20200301, 'ca',
          123, 5, 9, 8, 7, NULL, 20200301, 0, 1, False)
    ''')
    self.cnx.commit()

    # fill is_latest_issue
    main()

    self.cur.execute('''select * from covidcast''')
    result = list(self.cur)
    expected = [
        (1, 'src', 'sig', 'day', 'state', 20200228, 'ca',
          123, 2, 5, 5, 5, None, 20200228, 0, bytearray(b'0'), bytearray(b'0')),
        (2, 'src', 'sig', 'day', 'state', 20200228, 'ca',
          123, 2, 0, 0, 0, None, 20200229, 1, bytearray(b'1'), bytearray(b'0')),
        (3, 'src', 'sig', 'day', 'state', 20200229, 'ca',
          123, 6, 0, 0, 0, None, 20200301, 1, bytearray(b'1'), bytearray(b'0')),
        (4, 'src', 'sig', 'day', 'state', 20200229, 'ca',
          123, 6, 9, 9, 9, None, 20200229, 0, bytearray(b'0'), bytearray(b'0')),
        (5, 'src', 'sig', 'day', 'state', 20200301, 'ca',
          123, 5, 0, 0, 0, None, 20200303, 2, bytearray(b'1'), bytearray(b'0')),
        (6, 'src', 'sig', 'day', 'state', 20200301, 'ca',
          123, 5, 5, 5, 5, None, 20200302, 1, bytearray(b'0'), bytearray(b'0')),
        (7, 'src', 'sig', 'day', 'state', 20200301, 'ca',
          123, 5, 9, 8, 7, None, 20200301, 0, bytearray(b'0'), bytearray(b'0'))
    ]

    self.assertEqual(result, expected)
