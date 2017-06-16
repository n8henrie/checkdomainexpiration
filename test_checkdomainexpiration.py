import datetime
import unittest

import checkdomainexpiration

class TestCheckDomainExpiration(unittest.TestCase):
    def test_get_expiration_date(self):
        domain_info = """
                foo: bar
                Expiration Date: 13-Apr-2099
                BAZ: qux
                """
        dt = checkdomainexpiration.get_expiration_date(domain_info)

        self.assertEqual(dt, datetime.datetime(2099, 4, 13).date())
