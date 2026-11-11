from __future__ import absolute_import
import sys, os, unittest, weakref
sys.path.insert(0, os.path.dirname(__file__))
from test_core import Tests, Obj, module_at, mod


class NativePortrait(unittest.TestCase):
    def setUp(self):
        Tests.setUp.im_func(self)
        class Tankman(object):
            role = 'commander'
            invID = 10
            isInSkin = False
            def getExtensionLessIconWithSkin(self): return 'original_crew_icon'
            def getFullUserNameWithSkin(self): return 'Original Name'
        self.Tankman = Tankman
        module_at('gui.shared.gui_items.Tankman').Tankman = Tankman
        big = Obj(dyn=lambda name: lambda: 12345, crewSkins=Obj(dyn=lambda name: lambda: 12346))
        module_at('gui.impl.gen').R = Obj(images=Obj(gui=Obj(maps=Obj(icons=Obj(tankmen=Obj(icons=Obj(big=big)))))))
        mod.STATE = {'accounts': {'123': {'10': 'papacito'}}}
        mod.patch_native_portraits()

    def tearDown(self):
        Tests.tearDown.im_func(self)

    def test_native_portrait_is_selected_and_restored_per_commander(self):
        commander = self.Tankman()
        self.assertEqual(commander.getExtensionLessIconWithSkin(), 'custom_commander_papacito')
        self.assertEqual(commander.getFullUserNameWithSkin(), 'Papacito')
        other = self.Tankman(); other.invID = 11
        self.assertEqual(other.getExtensionLessIconWithSkin(), 'original_crew_icon')
        mod.STATE = {'accounts': {'123': {}}}
        self.assertEqual(commander.getExtensionLessIconWithSkin(), 'original_crew_icon')
        self.assertEqual(commander.getFullUserNameWithSkin(), 'Original Name')

    def test_disabled_portrait_preserves_native_appearance(self):
        mod.SETTINGS['portrait'] = False
        commander = self.Tankman()
        self.assertEqual(commander.getExtensionLessIconWithSkin(), 'original_crew_icon')
        self.assertEqual(commander.getFullUserNameWithSkin(), 'Original Name')

    def test_unknown_native_resource_preserves_original(self):
        big=module_at('gui.impl.gen').R.images.gui.maps.icons.tankmen.icons.big
        big.dyn=lambda name:lambda:-1
        self.assertEqual(self.Tankman().getExtensionLessIconWithSkin(),'original_crew_icon')

    def test_both_normal_and_equipped_appearance_use_the_same_local_icon(self):
        commander=self.Tankman()
        for equipped in (False, True):
            commander.isInSkin=equipped
            self.assertEqual(commander.getExtensionLessIconWithSkin(),'custom_commander_papacito')
            self.assertEqual(commander.isInSkin,equipped)

    def test_open_personal_file_refreshes_on_deactivation(self):
        commander=self.Tankman()
        class Info(object):
            def __init__(self):
                self.context=Obj(tankman=commander)
                self.viewModel=Obj()
                self.parent=Obj(viewModel=Obj())
            def _setTankmanInfo(self, model):
                model.icon=self.context.tankman.getExtensionLessIconWithSkin()
                model.name=self.context.tankman.getFullUserNameWithSkin()
            def refreshView(self):
                # ComponentBase commits the parent transaction in refreshView.
                self._setTankmanInfo(self.viewModel)
                self.rendered=(self.viewModel.icon,self.viewModel.name)
        module_at('gui.impl.lobby.crew.container_vews.common.tankman_info_component').TankmanInfoComponent=Info
        mod.patch_personal_file()
        component=Info();component.refreshView()
        self.assertEqual(component.viewModel.icon,'custom_commander_papacito')
        mod.STATE={'accounts':{'123':{}}}
        mod.PRESENTERS=[];mod.snapshot_current=lambda:None;mod.payload=lambda:'{}'
        self.originals['refresh']()
        self.assertEqual(component.viewModel.icon,'original_crew_icon')
        self.assertEqual(component.viewModel.name,'Original Name')
        self.assertEqual(component.rendered,('original_crew_icon','Original Name'))

    def test_cached_garage_model_refreshes_even_without_its_original_presenter(self):
        commander=self.Tankman()
        class Row(object):
            icon='custom_commander_papacito'
            name='Papacito'
            skin=False
            def getId(self):return 10
            def setCrewSkinId(self, value):self.icon=value
            def setFullName(self, value):self.name=value
            def setCustomizedSkin(self, value):self.skin=value
        class Crew(list):
            invalidated=False
            def invalidate(self):self.invalidated=True
        class Model(object):
            def __init__(self):self.crew=Crew([Row()]);self.rendered=('custom_commander_papacito','Papacito')
            def getCrew(self):return self.crew
            def transaction(self):return self
            def __enter__(self):return self
            def __exit__(self,*args):
                if self.crew.invalidated:self.rendered=(self.crew[0].icon,self.crew[0].name)
        model=Model()
        mod.CREW_MODELS=weakref.WeakSet([model]);mod.PRESENTERS=[]
        mod.INFO_COMPONENTS=weakref.WeakSet()
        mod.current_crew=lambda:(Obj(intCD=42),[(0,commander)])
        mod.snapshot_current=lambda:None;mod.payload=lambda:'{}'
        mod.STATE={'accounts':{'123':{}}}
        self.originals['refresh']()
        self.assertEqual(model.rendered,('original_crew_icon','Original Name'))
        mod.STATE={'accounts':{'123':{'10':'papacito'}}}
        self.originals['refresh']()
        self.assertEqual(model.rendered,('custom_commander_papacito','Papacito'))
        mod.SETTINGS['portrait']=False
        self.originals['refresh']()
        self.assertEqual(model.rendered,('original_crew_icon','Original Name'))
        self.assertTrue(mod.selected(10))


if __name__ == '__main__':
    unittest.main(defaultTest='NativePortrait')
