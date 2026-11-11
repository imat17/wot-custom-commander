"""Run with the installed Python 2.7, no code executed inside the game."""
from __future__ import print_function
import os, sys, py_compile, zipfile, hashlib
if sys.version_info[:2] != (2, 7):
    raise SystemExit('Python 2.7 is required for the WoT bytecode')
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dist = os.path.join(root, 'dist')
if not os.path.isdir(dist): os.makedirs(dist)
package = os.path.join(dist, 'matisse.commander_friend_0.2.5.wotmod')
with zipfile.ZipFile(package, 'w', zipfile.ZIP_STORED) as z:
    z.writestr('meta.xml', '<root><id>matisse.commander_friend</id><version>0.2.5</version><name>Custom Commander</name><description>Local commander portrait and voice prototype for WoT EU 2.4.1.1</description></root>')
    for name in ['mod_commander_friend', 'commander_friend_catalog']:
        src = os.path.join(root,'src',name+'.py')
        dest = os.path.join(dist,name+'.pyc')
        py_compile.compile(src, cfile=dest, dfile='commander_friend/'+name+'.py', doraise=True)
        sub = 'gui/mods/' if name.startswith('mod_') else ''
        z.write(dest, 'res/scripts/client/'+sub+name+'.pyc')
    z.write(os.path.join(root,'src','portrait.js'),'res/gui/gameface/mods/commander_friend/portrait.js')
    z.write(os.path.join(root,'src','resources.json'),'res/gui/gen_resources/matisse.commander_friend.json')
    z.write(os.path.join(root,'assets','demo.png'),'res/gui/maps/icons/commander_friend/demo.png')
    z.write(os.path.join(root,'assets','profiles','papacito','portrait.jpg'),
            'res/gui/maps/icons/commander_friend/profiles/papacito/portrait.jpg')
    for folder in ['', 'crewSkins/']:
        z.write(os.path.join(root,'assets','profiles','papacito','portrait.jpg'),
                'res/gui/maps/icons/tankmen/icons/big/'+folder+'commander_friend_papacito.jpg')
with zipfile.ZipFile(package) as z:
    assert z.testzip() is None
    assert all(i.compress_type==zipfile.ZIP_STORED for i in z.infolist())
with open(package,'rb') as f: digest=hashlib.sha256(f.read()).hexdigest()
print(package)
print('SHA256 '+digest)
