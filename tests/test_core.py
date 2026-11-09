from __future__ import absolute_import
import os, sys, unittest, tempfile, shutil, wave, types
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
import mod_commander_friend as mod

class Obj(object):
    def __init__(self, **kwargs): self.__dict__.update(kwargs)

def module_at(name):
    parts=name.split('.')
    for i in range(1,len(parts)+1):
        key='.'.join(parts[:i])
        if key not in sys.modules:
            sys.modules[key]=types.ModuleType(key)
            sys.modules[key].__path__=[]
        if i>1:setattr(sys.modules['.'.join(parts[:i-1])],parts[i-1],sys.modules[key])
    return sys.modules[name]

class Tests(unittest.TestCase):
    def setUp(self):
        self.originals = dict(mod.__dict__)
        self.temp = tempfile.mkdtemp()
        mod.ROOT = self.temp
        mod.STATE = {'accounts': {}}
        mod.account_id = lambda: '123'
        mod.refresh = lambda *args: None
        mod.notice = lambda message: None
        mod.PATCHES = []
        mod.PENDING_AUDIO = {}
        self.player = Obj(vehicleTypeDescriptor=Obj(type=Obj(compactDescr=42)))
        self.callbacks = {}
        bw = types.ModuleType('BigWorld')
        bw.player = lambda: self.player
        def callback(delay, cb):
            key=len(self.callbacks)+1; self.callbacks[key]=(delay,cb); return key
        bw.callback = callback
        bw.cancelCallback = lambda key: self.callbacks.pop(key,None)
        sys.modules['BigWorld'] = bw
        replay=types.ModuleType('BattleReplay'); replay.g_replayCtrl=Obj(isPlaying=False)
        sys.modules['BattleReplay']=replay

    def tearDown(self):
        mod.__dict__.update(self.originals)
        shutil.rmtree(self.temp)

    def test_toggle_is_per_commander_and_account_and_persistent(self):
        man=Obj(invID=10,role='commander')
        self.assertTrue(mod.toggle(man)); self.assertTrue(mod.selected(10))
        self.assertFalse(mod.selected(11)); self.assertFalse(mod.selected(10,'456'))
        self.assertTrue(os.path.isfile(os.path.join(self.temp,'selection.json')))
        self.assertTrue(mod.toggle(man)); self.assertFalse(mod.selected(10))
        self.assertFalse(mod.toggle(Obj(invID=11,role='driver')))

    def test_failed_save_reverts_choice(self):
        def fail(): raise IOError('test')
        mod.save_state=fail
        self.assertFalse(mod.toggle(Obj(invID=10,role='commander')))
        self.assertFalse(mod.selected(10))

    def test_no_account_does_not_personalize(self):
        mod.account_id=lambda:None
        self.assertFalse(mod.toggle(Obj(invID=10,role='commander')))

    def test_voice_scope_spectator_replay_wrong_tank_disabled(self):
        mod.SETTINGS=dict(mod.DEFAULTS);mod.SNAPSHOT=('123',42,[10]);mod.PLAYER_VEHICLE=True
        mod.STATE={'accounts':{'123':['10']}}
        self.assertTrue(mod.voice_active())
        mod.PLAYER_VEHICLE=False;self.assertFalse(mod.voice_active())
        mod.PLAYER_VEHICLE=True
        sys.modules['BattleReplay'].g_replayCtrl.isPlaying=True;self.assertFalse(mod.voice_active())
        sys.modules['BattleReplay'].g_replayCtrl.isPlaying=False
        self.player.vehicleTypeDescriptor.type.compactDescr=43;self.assertFalse(mod.voice_active())
        self.player.vehicleTypeDescriptor.type.compactDescr=42
        mod.SETTINGS['enabled']=False;self.assertFalse(mod.voice_active())

    def test_missing_wav_and_unsupported_format_retain_original(self):
        self.assertFalse(mod.play_wav(os.path.join(self.temp,'absent.wav')))
        p=os.path.join(self.temp,'bad.wav')
        w=wave.open(p,'wb');w.setnchannels(1);w.setsampwidth(1);w.setframerate(8000);w.writeframes(b'\0'*800);w.close()
        mod.SOUND=lambda *args: self.fail('invalid WAV must not play')
        self.assertFalse(mod.play_wav(p))

    def test_native_queue_completion_and_cancellation(self):
        mod.voice_active=lambda:True
        calls=[]
        manager=Obj(isCategoryEnabled=lambda c:True,onNotificationBegins=lambda n:calls.append(('start',n)),
            getEventInfo=lambda n,p:'2',setEventCooldown=lambda n,t:calls.append(('cooldown',t)),
            playNextQueueEvent=lambda q:calls.append(('next',q)))
        p=os.path.join(self.temp,'valid.wav')
        w=wave.open(p,'wb');w.setnchannels(1);w.setsampwidth(2);w.setframerate(8000);w.writeframes(b'\0'*1600);w.close()
        mod.sound_file=lambda filename:p;mod.SOUND=lambda *args:1
        self.assertFalse(mod.play_queued(manager,1,'not_a_game_event'))
        self.assertFalse(mod.play_queued(manager,2,'start_battle'))
        self.assertTrue(mod.play_queued(manager,1,'start_battle'))
        key=mod.PENDING_AUDIO[id(manager)];delay,cb=self.callbacks.pop(key)
        self.assertAlmostEqual(delay,.15);cb();self.assertIn(('next',1),calls)
        self.assertNotIn(id(manager),mod.PENDING_AUDIO)
        self.assertTrue(mod.play_queued(manager,1,'start_battle'))
        mod.cancel_audio(manager);self.assertFalse(self.callbacks)

    def test_context_menu_preserves_native_options(self):
        class Handler(object):
            def _generateOptions(self,ctx=None):return ['native']
            def onOptionSelect(self,key):return 'native:'+key
            def _makeItem(self,key,label):return {'id':key,'label':label}
        module=module_at('gui.impl.lobby.crew.widget.crew_widget_cm_handlers')
        module.CrewContextMenuHandler=Handler
        sys.modules[module.__name__]=module
        mod.patch_context_menu()
        h=Handler();h._tankman=Obj(invID=10,role='commander')
        self.assertEqual(h._generateOptions()[0],'native')
        self.assertEqual(h._generateOptions()[-1]['id'],mod.ACTION)
        h.onOptionSelect(mod.ACTION);self.assertTrue(mod.selected(10))
        self.assertEqual(h.onOptionSelect('personalFile'),'native:personalFile')
        h._tankman.role='driver';self.assertEqual(h._generateOptions(),['native'])

    def test_queue_wrapper_preserves_native_checks_and_fallback(self):
        calls=[]
        class Notifications(object):
            def __init__(self):self.onPlayEvent=lambda name:calls.append(name)
            def __playFirstFromQueue(self,queue):
                calls.append('native_checks')
                if self.allowed:self.onPlayEvent('start_battle')
            def playNextQueueEvent(self,queue):pass
            def clear(self):pass
        # Class name mangling matches the real class explicitly.
        Notifications._IngameSoundNotifications__playFirstFromQueue=Notifications._Notifications__playFirstFromQueue
        module_at('gui.IngameSoundNotifications').IngameSoundNotifications=Notifications
        class Ctrl(object):
            def setPlayerVehicle(self,info,own):pass
        module_at('gui.game_control.special_sound_ctrl').SpecialSoundCtrl=Ctrl
        mod.patch_voice()
        n=Notifications();emitter=n.onPlayEvent;n.allowed=False
        mod.play_queued=lambda *args:self.fail('rejected event must not play')
        n._IngameSoundNotifications__playFirstFromQueue(1)
        self.assertEqual(calls,['native_checks']);self.assertIs(n.onPlayEvent,emitter)
        calls[:]=[];n.allowed=True;mod.play_queued=lambda *args:False
        n._IngameSoundNotifications__playFirstFromQueue(1)
        self.assertEqual(calls,['native_checks','start_battle'])
        calls[:]=[];mod.play_queued=lambda *args:True
        n._IngameSoundNotifications__playFirstFromQueue(1)
        self.assertEqual(calls,['native_checks']);self.assertIs(n.onPlayEvent,emitter)

if __name__=='__main__':unittest.main()
