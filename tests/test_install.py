#!/usr/bin/env python3

import unittest

import gbm


class TestInstall(unittest.TestCase):
    def test_install(self):
        # Just do something with gbm to see it has imported ok
        self.assertEqual(gbm.GBM_FORMAT_XRGB8888, 0x34325258)


if __name__ == '__main__':
    unittest.main()
