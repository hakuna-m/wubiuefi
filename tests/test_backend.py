# tools/pywine -O tests/test_backend.py
import unittest
import sys, os
sys.path.insert(0, 'build\\wubi\\lib')
from wubi.backends.win32 import backend
from version import application_name, version, revision
from wubi import application

import mock
from wubi.backends.win32 import registry
class BackendTests(unittest.TestCase):
    def setUp(self):
        w = application.Wubi(application_name, version,
                             revision, 'build\\wubi')
        # To get things like info.locale set.
        w.parse_commandline_arguments()
        self.back = backend.WindowsBackend(w)
        w.info.original_exe = os.path.join(os.getcwd(), 'build', 'wubi.exe')

        # Data
        self.uninstall_keys = [
            ('HKEY_LOCAL_MACHINE', 'registry-key', 'UninstallString',
             'Z:\\tmp\\uninstall-wubi.exe'),
            ('HKEY_LOCAL_MACHINE', 'registry-key', 'InstallationDir', '/tmp'),
            ('HKEY_LOCAL_MACHINE', 'registry-key', 'DisplayName', 'Ubuntu'),
            ('HKEY_LOCAL_MACHINE', 'registry-key', 'DisplayIcon',
             os.path.join(os.getcwd(), 'build\\wubi\\data\\images\\Wubi.ico')),
            ('HKEY_LOCAL_MACHINE', 'registry-key', 'DisplayVersion',
             self.back.info.version_revision),
            ('HKEY_LOCAL_MACHINE', 'registry-key', 'Publisher', 'Ubuntu'),
            ('HKEY_LOCAL_MACHINE', 'registry-key', 'URLInfoAbout',
             'http://www.ubuntu.com'),
            ('HKEY_LOCAL_MACHINE', 'registry-key', 'HelpLink',
             'http://www.ubuntu.com/support')]
        # Python2.3 doesn't have addCleanup (2.7), so we need to manage
        # cleaning up after this mock ourselves.
        self.save_registry = registry.set_value
        # Patch away!
        registry.set_value = mock.Mock()
    
    def tearDown(self):
        registry.set_value = self.save_registry

    def test_create_uninstaller(self):
        # We don't have decorators in Python 2.3, so we can't use mock.patch
        # here.
        self.back.info.target_dir = '/tmp'
        self.back.info.registry_key = 'registry-key'
        self.back.info.distro = self.back.parse_isolist(
                                    'build/wubi/data/isolist.ini')[0]
        self.back.create_uninstaller(None)
        calls = registry.set_value.call_args_list
        remove = []
        for c in calls:
            if c[0] in self.uninstall_keys:
                remove.append(c)
            else:
                self.fail('Did not expect key to be set: %s' % str(c[0]))
        for r in remove:
            calls.remove(r)
        self.assert_(len(calls) == 0,
            'Did not set required registry keys:\n%s' % str(calls))
        # TODO mktempd
        self.assert_(os.path.exists('/tmp/uninstall-wubi.exe'),
            'Did not install uninstaller binary.')
        os.remove('/tmp/uninstall-wubi.exe')

    def test_get_iso_file(self):
        # http://pad.lv/856340
        expected = ['%02d' % x for x in range(1,51)]
        self.assertEqual(expected,
            self.back.get_iso_file_names('tests/data/small.iso'))

if __name__ == '__main__':
    unittest.main()
