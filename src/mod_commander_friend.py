# coding: utf-8
"""Commander Friend 0.1.1 -- WoT EU 2.4.1.1, local cosmetic prototype."""
from __future__ import absolute_import
import json
import logging
import os
import wave

LOG = logging.getLogger('CommanderFriend')
LINKAGE = 'matisse.commander_friend'
ACTION = 'commanderFriendToggle'
ROOT = os.path.abspath(os.path.join('mods', 'configs', LINKAGE))
AUDIO_PATH = os.path.join(ROOT, 'native_0.1.1', 'commander_friend_audio.pyd')
DEFAULTS = {'enabled': True, 'portrait': True, 'voice': True, 'demo': True}
SETTINGS = dict(DEFAULTS)
STATE = {'accounts': {}}
PRESENTERS = []
PATCHES = []
SUBSCRIPTIONS = []
API = None
TEMPLATES = None
CALLBACK = None
STARTED = False
SNAPSHOT = None
PLAYER_VEHICLE = False
SOUND = None
PENDING_AUDIO = {}

# These are notification IDs, not arbitrary sound effects. Missing WAVs retain
# the native notification. This prototype never changes the account/crew data.
EVENT_FILES = {
    'battle_start': 'battle_start.wav',
    'enemy_killed': 'enemy_killed.wav',
    'enemy_hp_damaged_by_projectile_by_player': 'penetration.wav',
    'track_destroyed': 'track_destroyed.wav',
    'track_functional': 'track_functional.wav',
    'vehicle_destroyed': 'vehicle_destroyed.wav',
}
try:
    from commander_friend_catalog import EVENT_FILES
except ImportError:
    pass


def account_id():
    import BigWorld
    player = BigWorld.player()
    value = getattr(player, 'databaseID', 0) if player else 0
    return str(value) if value and value > 0 else None


def selected(tankman_id, owner=None):
    owner = owner or account_id()
    return bool(owner and str(tankman_id) in STATE['accounts'].get(owner, []))


def save_state():
    if not os.path.isdir(ROOT):
        os.makedirs(ROOT)
    path = os.path.join(ROOT, 'selection.json')
    temp = path + '.tmp'
    with open(temp, 'wb') as stream:
        stream.write(json.dumps(STATE, sort_keys=True, indent=2).encode('utf8'))
        stream.flush()
        os.fsync(stream.fileno())
    # Python 2 Windows rename cannot replace an existing destination. Keep the
    # last committed file as a recovery copy until the new one has been renamed.
    backup = path + '.bak'
    if os.path.isfile(path):
        if os.path.isfile(backup):
            os.remove(backup)
        os.rename(path, backup)
    try:
        os.rename(temp, path)
    except Exception:
        if not os.path.isfile(path) and os.path.isfile(backup):
            os.rename(backup, path)
        raise


def load_state():
    path = os.path.join(ROOT, 'selection.json')
    # Recover a process interruption between the two rename operations.
    if not os.path.isfile(path):
        path += '.bak'
    if not os.path.isfile(path):
        return {'accounts': {}}
    with open(path, 'rb') as stream:
        data = json.load(stream)
    if not isinstance(data, dict) or not isinstance(data.get('accounts'), dict):
        raise ValueError('Invalid selection file')
    return data


def notice(text):
    from gui import SystemMessages
    SystemMessages.pushMessage(text, type=SystemMessages.SM_TYPE.Information)


def toggle(tman):
    owner = account_id()
    if not owner or not tman or tman.role != 'commander':
        return False
    before = list(STATE['accounts'].get(owner, []))
    values = list(before)
    key = str(tman.invID)
    if key in values:
        values.remove(key)
    else:
        values.append(key)
    STATE['accounts'][owner] = values
    try:
        save_state()
    except Exception:
        STATE['accounts'][owner] = before
        LOG.exception('Cannot persist selection')
        notice(u'Chef de char ami : impossible de sauvegarder le choix.')
        return False
    refresh()
    LOG.info('Commander customization %s', 'enabled' if key in values else 'disabled')
    notice(u'Personnalisation activée pour ce chef de char.' if key in values else
           u'Personnalisation retirée pour ce chef de char.')
    return True


def current_crew():
    from CurrentVehicle import g_currentVehicle
    vehicle = g_currentVehicle.item
    if not vehicle:
        return None, []
    return vehicle, list(vehicle.crew)


def portrait_url():
    if SETTINGS.get('demo', True):
        return 'coui://gui/maps/icons/commander_friend/demo.png'
    # A prepared PNG is stored loose in the versioned resource directory.
    import ResMgr
    path = 'gui/maps/icons/commander_friend/friend.png'
    if ResMgr.isFile(path):
        return 'coui://' + path
    return ''


def payload():
    vehicle, crew = current_crew()
    slots = []
    if SETTINGS.get('enabled') and SETTINGS.get('portrait'):
        slots = [slot for slot, man in crew if man and man.role == 'commander' and selected(man.invID)]
    return json.dumps({'slots': slots, 'portrait': portrait_url(), 'demo': SETTINGS.get('demo', True)})


def snapshot_current():
    global SNAPSHOT
    vehicle, crew = current_crew()
    owner = account_id()
    # Do not replace a valid garage snapshot while Account changes to Avatar.
    if owner and vehicle:
        ids = [man.invID for _, man in crew if man and man.role == 'commander']
        SNAPSHOT = (owner, vehicle.intCD, ids)


def account_entered(*args):
    global SNAPSHOT
    SNAPSHOT = None
    refresh()


def refresh(*args):
    try:
        snapshot_current()
        data = payload()
        for presenter in list(PRESENTERS):
            presenter.viewModel._setString(11, data)
    except Exception:
        LOG.exception('Unable to refresh garage portrait')


def sound_file(filename):
    folder = 'demo_voice' if SETTINGS.get('demo', True) else 'voice'
    return os.path.join(ROOT, folder, filename)


def play_wav(path):
    global SOUND
    if not os.path.isfile(path):
        return False
    try:
        stream = wave.open(path, 'rb')
        try:
            if stream.getcomptype() != 'NONE' or stream.getsampwidth() != 2 or stream.getnchannels() not in (1, 2):
                return False
            if not 0 < stream.getnframes() / float(stream.getframerate()) <= 15:
                return False
        finally:
            stream.close()
        if SOUND is None:
            import imp
            audio = imp.load_dynamic('commander_friend_audio', AUDIO_PATH)
            SOUND = audio.play_sound
            LOG.info('Windows audio backend loaded')
        # SND_FILENAME | SND_ASYNC | SND_NODEFAULT; no executable loading.
        return bool(SOUND(unicode(path), None, 0x20000 | 0x1 | 0x2))
    except Exception:
        LOG.exception('Unable to play WAV; keeping native voice')
        return False


def stop_sound(*args):
    global PLAYER_VEHICLE
    PLAYER_VEHICLE = False
    if SOUND is not None:
        SOUND(None, None, 0)


def cancel_audio(manager):
    import BigWorld
    pending = PENDING_AUDIO.pop(id(manager), None)
    if pending:
        BigWorld.cancelCallback(pending)
        if SOUND is not None:
            SOUND(None, None, 0)


def play_queued(manager, queue, event_name):
    """Called only AFTER the native queue's predicates/lifetime/priority checks."""
    if queue != 1 or not voice_active() or not manager.isCategoryEnabled('voice'):
        return False
    filename = EVENT_FILES.get(event_name)
    if not filename:
        return False
    path = sound_file(filename)
    try:
        stream = wave.open(path, 'rb')
        try:
            duration = stream.getnframes() / float(stream.getframerate())
        finally:
            stream.close()
    except (IOError, EOFError, wave.Error):
        return False
    if not play_wav(path):
        return False
    import BigWorld
    manager.onNotificationBegins(event_name)
    cooldown = manager.getEventInfo(event_name, 'cooldownEvent')
    if cooldown:
        manager.setEventCooldown(event_name, float(cooldown))
    def completed():
        PENDING_AUDIO.pop(id(manager), None)
        manager.playNextQueueEvent(queue)
    PENDING_AUDIO[id(manager)] = BigWorld.callback(duration + 0.05, completed)
    return True


def voice_active():
    if not SETTINGS.get('enabled') or not SETTINGS.get('voice') or not SNAPSHOT or not PLAYER_VEHICLE:
        return False
    import BigWorld
    import BattleReplay
    if BattleReplay.g_replayCtrl.isPlaying:
        return False
    player = BigWorld.player()
    descriptor = getattr(player, 'vehicleTypeDescriptor', None)
    if descriptor is None or descriptor.type.compactDescr != SNAPSHOT[1]:
        return False
    return any(selected(key, SNAPSHOT[0]) for key in SNAPSHOT[2])


def patch(cls, name, factory):
    previous = getattr(cls, name)
    replacement = factory(previous)
    setattr(cls, name, replacement)
    PATCHES.append((cls, name, previous, replacement))


def patch_context_menu():
    from gui.impl.lobby.crew.widget.crew_widget_cm_handlers import CrewContextMenuHandler
    def options_factory(original):
        def options(self, ctx=None):
            result = original(self, ctx)
            man = getattr(self, '_tankman', None)
            if man and man.role == 'commander' and account_id():
                label = u'Retirer la personnalisation ami' if selected(man.invID) else u'Activer la personnalisation ami'
                result.append(self._makeItem(ACTION, label))
            return result
        return options
    def select_factory(original):
        def on_select(self, option):
            if option == ACTION:
                toggle(getattr(self, '_tankman', None))
                return
            return original(self, option)
        return on_select
    patch(CrewContextMenuHandler, '_generateOptions', options_factory)
    patch(CrewContextMenuHandler, 'onOptionSelect', select_factory)


def patch_portraits():
    from gui.impl.gen.view_models.views.lobby.loadout.crew.crew_model import CrewModel
    from gui.impl.lobby.hangar.presenters.crew_presenter import CrewPresenter
    from openwg_gameface import gf_mod_inject
    def init_factory(original):
        def initialize(self, properties=10, commands=5):
            return original(self, properties=properties + 2, commands=commands)
        return initialize
    def model_factory(original):
        def initialize(self):
            original(self)
            gf_mod_inject(self, 'CommanderFriend', scripts=['coui://gui/gameface/mods/commander_friend/portrait.js'])
            self._addStringProperty('commanderFriendJson', '{}')
        return initialize
    def load_factory(original):
        def loaded(self, *args, **kwargs):
            result = original(self, *args, **kwargs)
            if self not in PRESENTERS:
                PRESENTERS.append(self)
            refresh()
            return result
        return loaded
    def update_factory(original):
        def updated(self, *args, **kwargs):
            result = original(self, *args, **kwargs)
            self.viewModel._setString(11, payload())
            snapshot_current()
            return result
        return updated
    def final_factory(original):
        def finalized(self, *args, **kwargs):
            if self in PRESENTERS:
                PRESENTERS.remove(self)
            return original(self, *args, **kwargs)
        return finalized
    patch(CrewModel, '__init__', init_factory)
    patch(CrewModel, '_initialize', model_factory)
    patch(CrewPresenter, '_onLoading', load_factory)
    patch(CrewPresenter, '_CrewPresenter__updateModel', update_factory)
    patch(CrewPresenter, 'finalize', final_factory)


def patch_voice():
    from gui.IngameSoundNotifications import IngameSoundNotifications
    from gui.game_control.special_sound_ctrl import SpecialSoundCtrl
    def vehicle_factory(original):
        def switched(self, info, own):
            global PLAYER_VEHICLE
            result = original(self, info, own)
            PLAYER_VEHICLE = bool(own)
            if not own and SOUND is not None:
                SOUND(None, None, 0)
            return result
        return switched
    def queue_factory(original):
        def dispatch(self, queue):
            emitter = self.onPlayEvent
            def emit(name):
                try:
                    if play_queued(self, queue, name):
                        return
                except Exception:
                    LOG.exception('Custom voice failed; returning to native voice')
                    cancel_audio(self)
                    if SOUND is not None:
                        SOUND(None, None, 0)
                return emitter(name)
            self.onPlayEvent = emit
            try:
                return original(self, queue)
            finally:
                self.onPlayEvent = emitter
        return dispatch
    def clear_factory(original):
        def clear(self, *args, **kwargs):
            cancel_audio(self)
            return original(self, *args, **kwargs)
        return clear
    def next_factory(original):
        def next_event(self, queue):
            if queue == 1:
                cancel_audio(self)
            return original(self, queue)
        return next_event
    patch(SpecialSoundCtrl, 'setPlayerVehicle', vehicle_factory)
    patch(IngameSoundNotifications, '_IngameSoundNotifications__playFirstFromQueue', queue_factory)
    patch(IngameSoundNotifications, 'playNextQueueEvent', next_factory)
    patch(IngameSoundNotifications, 'clear', clear_factory)


def settings_changed(linkage, values):
    if linkage != LINKAGE:
        return
    SETTINGS.update(dict((key, bool(values.get(key, DEFAULTS[key]))) for key in DEFAULTS))
    if SOUND is not None:
        SOUND(None, None, 0)
    refresh()


def button_clicked(linkage, name, value):
    if linkage != LINKAGE:
        return
    if name == 'preview':
        if not play_wav(sound_file(EVENT_FILES.get('start_battle', 'vo_start_battle.wav'))):
            notice(u'Lecture impossible : vérifiez le fichier vocal et le journal CommanderFriend.')
        else:
            LOG.info('Voice preview started')
    elif name == 'folder':
        if not os.path.isdir(ROOT):
            os.makedirs(ROOT)
        os.startfile(ROOT)
    elif name == 'catalogue':
        path = os.path.join(ROOT, 'Catalogue-des-enregistrements.html')
        if os.path.isfile(path):
            os.startfile(path)
    elif name == 'portraitFolder':
        path = os.path.abspath(os.path.join('res_mods', '2.4.1.1', 'gui', 'maps', 'icons', 'commander_friend'))
        if not os.path.isdir(path):
            os.makedirs(path)
        os.startfile(path)
    elif name == 'toggleCurrent':
        _, crew = current_crew()
        for _, man in crew:
            if man and man.role == 'commander':
                toggle(man)
                break


def register_settings(attempt=0):
    global API, TEMPLATES, CALLBACK
    CALLBACK = None
    try:
        from gui.aslainMenu import g_modsSettingsApi, templates
        API, TEMPLATES = g_modsSettingsApi, templates
        t = templates
        form = {
            'modDisplayName': u'Chef de char ami', 'modAuthor': 'Matisse',
            'modVersion': '0.1.1 alpha', 'settingsVersion': 1,
            'enabled': SETTINGS['enabled'],
            'column1': [
                t.createLabel(u'Clic droit sur un chef de char : activer ou retirer la personnalisation.'),
                t.createCheckbox(u'Portrait dans le garage', 'portrait', SETTINGS['portrait']),
                t.createCheckbox(u'Répliques personnalisées', 'voice', SETTINGS['voice']),
                t.createCheckbox(u'Utiliser les médias de démonstration', 'demo', SETTINGS['demo']),
                t.createLabel(u'Démo : silhouette et voix synthétique. Mode personnel : vos fichiers.'),
            ],
            'column2': [
                t.createActionButton('preview', buttonText=u'Écouter', label=u'Réplique de départ'),
                t.createActionButton('folder', buttonText=u'Ouvrir', label=u'Dossier des enregistrements'),
                t.createActionButton('portraitFolder', buttonText=u'Ouvrir', label=u'Dossier de la photo : friend.png'),
                t.createActionButton('catalogue', buttonText=u'Consulter', label=u'Liste des répliques à enregistrer'),
                t.createActionButton('toggleCurrent', buttonText=u'Activer / retirer', label=u'Chef du char sélectionné'),
                t.createLabel(u'Prototype : portrait du garage uniquement. Audio WAV via Windows ; volume du mélangeur Windows.'),
            ],
        }
        values = API.setModTemplate(LINKAGE, form, settings_changed, button_clicked)
        settings_changed(LINKAGE, values or DEFAULTS)
        LOG.info('Settings registered')
    except ImportError:
        if attempt < 10:
            import BigWorld
            CALLBACK = BigWorld.callback(1.0, lambda: register_settings(attempt + 1))
        else:
            LOG.error('Aslain Mod Menu unavailable')


def init():
    global STARTED, STATE
    if STARTED:
        return
    try:
        STATE = load_state()
        patch_context_menu()
        patch_portraits()
        patch_voice()
        from CurrentVehicle import g_currentVehicle
        from PlayerEvents import g_playerEvents
        for event, callback in [(g_currentVehicle.onChanged, refresh),
                                (g_playerEvents.onAccountBecomePlayer, account_entered),
                                (g_playerEvents.onAvatarBecomeNonPlayer, stop_sound)]:
            event += callback
            SUBSCRIPTIONS.append((event, callback))
        STARTED = True
        register_settings()
        LOG.info('0.1.1 alpha initialized')
    except Exception:
        LOG.exception('Initialization failed; rolling back hooks')
        fini()


def fini():
    global STARTED, CALLBACK, SNAPSHOT
    stop_sound()
    import BigWorld
    for pending in PENDING_AUDIO.values():
        BigWorld.cancelCallback(pending)
    PENDING_AUDIO.clear()
    if CALLBACK is not None:
        import BigWorld
        BigWorld.cancelCallback(CALLBACK)
        CALLBACK = None
    for event, callback in SUBSCRIPTIONS:
        event -= callback
    del SUBSCRIPTIONS[:]
    for cls, name, original, installed in reversed(PATCHES):
        if getattr(cls, name) is installed:
            setattr(cls, name, original)
    del PATCHES[:]
    del PRESENTERS[:]
    SNAPSHOT = None
    STARTED = False
