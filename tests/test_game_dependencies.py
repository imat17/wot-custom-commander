"""Reproduce the missing _ctypes failure seen in the actual game log."""
import __builtin__
import os
import sys
import shutil
import tempfile
import unittest
import wave
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
import mod_commander_friend as mod


class GameDependencies(unittest.TestCase):
    def setUp(self):
        self.originals = dict(mod.__dict__)
        self.root = tempfile.mkdtemp()
        mod.ROOT = self.root
        mod.STATE = {'accounts': {}}
        mod.account_id = lambda: 'test-account'
        mod.refresh = lambda: None
        mod.notice = lambda message: None
        mod.SOUND = None
        self.real_import = __builtin__.__import__
        def game_import(name, *args, **kwargs):
            if name in ('ctypes', '_ctypes'):
                raise ImportError('No module named _ctypes')
            return self.real_import(name, *args, **kwargs)
        __builtin__.__import__ = game_import

    def tearDown(self):
        __builtin__.__import__ = self.real_import
        mod.__dict__.update(self.originals)
        shutil.rmtree(self.root)

    def test_activation_without_ctypes(self):
        man = type('Commander', (object,), {'invID': 10, 'role': 'commander'})()
        self.assertTrue(mod.toggle(man), 'right-click must activate without ctypes')
        self.assertTrue(mod.selected(10))
        self.assertEqual(mod.load_state(), mod.STATE)
        self.assertTrue(mod.toggle(man), 'second click must persist deactivation')
        self.assertFalse(mod.selected(10))
        self.assertEqual(mod.load_state(), mod.STATE)

    def test_failed_replacement_preserves_committed_selection(self):
        mod.STATE = {'accounts': {'test-account': ['10']}}
        mod.save_state()
        committed = mod.load_state()
        mod.STATE = {'accounts': {'test-account': ['11']}}
        original = os.rename
        def fail_commit(source, target):
            if source.endswith('.tmp'):
                raise IOError('simulated failure')
            return original(source, target)
        os.rename = fail_commit
        try:
            self.assertRaises(IOError, mod.save_state)
        finally:
            os.rename = original
        self.assertEqual(mod.load_state(), committed)

    def test_interrupted_save_recovers_previous_selection(self):
        mod.STATE = {'accounts': {'test-account': ['10']}}
        mod.save_state()
        path = os.path.join(self.root, 'selection.json')
        os.rename(path, path + '.bak')
        self.assertEqual(mod.load_state(), mod.STATE)

    def test_real_wav_playback_without_ctypes(self):
        # Load the built native module from its stable test location, so Windows
        # does not keep a DLL locked inside the disposable temp directory.
        mod.AUDIO_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..',
                                      'dist', 'native_0.1.1', 'commander_friend_audio.pyd'))
        path = os.path.join(self.root, 'silent.wav')
        stream = wave.open(path, 'wb')
        try:
            stream.setnchannels(1)
            stream.setsampwidth(2)
            stream.setframerate(8000)
            stream.writeframes(b'\0' * 1600)
        finally:
            stream.close()
        self.assertTrue(mod.play_wav(path), 'valid WAV must reach Windows playback')
        mod.stop_sound()


if __name__ == '__main__':
    unittest.main()
