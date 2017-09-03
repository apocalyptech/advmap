#!/usr/bin/env python3
# vim: set expandtab tabstop=4 shiftwidth=4:

import unittest

if __name__ == '__main__':

    # I actually don't know why just 'unittest.main()' doesn't work here.
    # From the commandline you can run tests just by doing:
    #
    #   $ python -m unittest
    #
    # ... and it finds the tests in the 'test' dir just fine.  Using
    # unittest.main() doesn't, though - we've gotta manually call that
    # discover() method, apparently.  Ah well, whatever.

    #unittest.main()
    testsuite = unittest.TestLoader().discover('.')
    unittest.TextTestRunner(verbosity=1).run(testsuite)
