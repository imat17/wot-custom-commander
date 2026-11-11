from __future__ import absolute_import
import os, sys, unittest, tempfile, shutil, wave, types, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
import mod_custom_commander as mod

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
        mod.SETTINGS = dict(mod.DEFAULTS, profile=0)
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
        mod.sound_file=lambda filename, profile=None:p;mod.SOUND=lambda *args:1
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
        self.assertEqual(h._generateOptions()[1]['id'],mod.PROFILE_ACTION+'papacito')
        h.onOptionSelect(mod.PROFILE_ACTION+'papacito');self.assertEqual(mod.selected_profile(10),'papacito')
        # Choosing an already active profile is idempotent, not a toggle.
        h.onOptionSelect(mod.PROFILE_ACTION+'papacito');self.assertTrue(mod.selected(10))
        self.assertEqual(h._generateOptions()[-1]['id'],mod.ACTION)
        h.onOptionSelect(mod.ACTION);self.assertFalse(mod.selected(10))
        self.assertEqual(h.onOptionSelect('personalFile'),'native:personalFile')
        h._tankman.role='driver';self.assertEqual(h._generateOptions(),['native'])

    def test_profiles_persist_per_commander_without_changing_other_selections(self):
        mod.STATE={'accounts':{'123':['10','11'], '456':['10']}}
        man=Obj(invID=10,role='commander')
        self.assertEqual(mod.selected_profile(10),'legacy')
        self.assertTrue(mod.assign_profile(man,'papacito'))
        self.assertEqual(mod.selected_profile(10),'papacito')
        self.assertEqual(mod.selected_profile(11),'legacy')
        self.assertEqual(mod.selected_profile(10,'456'),'legacy')
        self.assertEqual(mod.load_state(),mod.STATE)
        self.assertTrue(mod.assign_profile(man,None))
        self.assertFalse(mod.selected(10));self.assertTrue(mod.selected(11))
        self.assertFalse(mod.assign_profile(man,'../invalid'))

    def test_profile_controls_portrait_and_battle_audio_independently_of_preview(self):
        man=Obj(invID=10,role='commander')
        mod.current_crew=lambda:(Obj(intCD=42),[(0,man),(1,Obj(invID=11,role='driver'))])
        mod.STATE={'accounts':{'123':{'10':'papacito'}}}
        data=json.loads(self.originals['payload']())
        self.assertEqual(data['slots'],[0]);self.assertEqual(data['name'],'Papacito')
        self.assertTrue(data['portrait'].endswith('profiles/papacito/portrait.jpg'))
        mod.SNAPSHOT=('123',42,[10])
        mod.SETTINGS['profile']=1
        self.assertEqual(mod.preview_profile(),'legacy')
        self.assertEqual(mod.battle_profile(),'papacito')
        path=mod.sound_file('vo_start_battle.wav',mod.battle_profile())
        self.assertIn(os.path.join('profiles','papacito','voice'),path)
        mod.STATE={'accounts':{'123':{'11':'papacito'}}}
        self.assertIsNone(mod.battle_profile())
        self.assertEqual(json.loads(self.originals['payload']())['slots'],[])

    def test_papacito_recordings_match_real_event_catalogue_and_missing_clip_falls_back(self):
        profile=os.path.join(os.path.dirname(__file__),'..','assets','profiles','papacito')
        with open(os.path.join(profile,'profile.json'),'rb') as stream: manifest=json.load(stream)
        self.assertEqual(len(manifest['recordings']),7)
        for row in manifest['recordings']:
            self.assertEqual(mod.EVENT_FILES[row['event']],row['file'])
            wav=wave.open(os.path.join(profile,'voice',row['file']),'rb')
            try:
                self.assertEqual(wav.getsampwidth(),2)
                self.assertTrue(0 < wav.getnframes()/float(wav.getframerate()) <= 15)
            finally: wav.close()
        mod.ROOT=os.path.abspath(os.path.join(profile,'..','..'))
        mod.SNAPSHOT=('123',42,[10]);mod.STATE={'accounts':{'123':{'10':'papacito'}}}
        mod.voice_active=lambda:True
        mod.SOUND=lambda *args:self.fail('missing clip must keep native voice')
        manager=Obj(isCategoryEnabled=lambda category:True)
        self.assertFalse(mod.play_queued(manager,1,'commander_killed'))
        played=[]
        mod.SOUND=lambda path, unused, flags:played.append(path) or 1
        manager.onNotificationBegins=lambda name:None
        manager.getEventInfo=lambda *args:None
        manager.playNextQueueEvent=lambda queue:None
        for row in manifest['recordings']:
            self.assertTrue(mod.play_queued(manager,1,row['event']))
            self.assertEqual(os.path.basename(played[-1]),row['file'])
            mod.cancel_audio(manager)

    def test_profile_change_failure_restores_previous_profile(self):
        mod.STATE={'accounts':{'123':{'10':'legacy'}}}
        def fail(): raise IOError('simulated disk failure')
        mod.save_state=fail
        self.assertFalse(mod.assign_profile(Obj(invID=10,role='commander'),'papacito'))
        self.assertEqual(mod.selected_profile(10),'legacy')

    def test_papacito_covers_ricochet_and_non_penetrating_armor_hits(self):
        mod.ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),'..','assets'))
        mod.SNAPSHOT=('123',42,[10]);mod.STATE={'accounts':{'123':{'10':'papacito'}}}
        mod.voice_active=lambda:True
        played=[]
        mod.SOUND=lambda path, unused, flags:played.append(path) or 1
        manager=Obj(isCategoryEnabled=lambda category:True,onNotificationBegins=lambda name:None,
                    getEventInfo=lambda *args:None,playNextQueueEvent=lambda queue:None)
        for event in ['enemy_ricochet_by_player','enemy_no_piercing_by_player',
                      'enemy_no_hp_damage_at_attempt_by_player',
                      'frequent_enemy_ricochet_by_player','frequent_enemy_no_piercing_by_player',
                      'frequent_enemy_no_hp_damage_at_attempt_by_player']:
            self.assertTrue(mod.play_queued(manager,1,event), event)
            with open(played[-1],'rb') as stream: actual=stream.read()
            with open(mod.sound_file('vo_armor_ricochet_by_player.wav','papacito'),'rb') as stream:
                self.assertEqual(actual,stream.read())
            mod.cancel_audio(manager)

    def test_return_to_garage_skips_unloaded_presenter_and_refreshes_new_one(self):
        updates=[]
        stale=Obj(viewModel=None)
        live=Obj(viewModel=Obj(_setString=lambda index,data:updates.append((index,data))))
        mod.PRESENTERS=[stale,live]
        mod.snapshot_current=lambda:None
        mod.payload=lambda:'{"slots":[0],"name":"Papacito"}'
        self.originals['refresh']()
        self.assertEqual(updates,[(11,mod.payload())])
        # A temporarily detached presenter may become usable later.
        stale.viewModel=Obj(_setString=lambda index,data:updates.append((index,data)))
        self.originals['refresh']()
        self.assertEqual(len(updates),3)

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
