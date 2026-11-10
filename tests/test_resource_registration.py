"""Verify the shipped native portrait can be resolved through WoT's image catalog."""
from __future__ import print_function
import json, sys, zipfile

with zipfile.ZipFile(sys.argv[1]) as package:
    descriptor = 'res/gui/gen_resources/matisse.commander_friend.json'
    assert descriptor in package.namelist(), 'Native image declarations are missing from the mod package'
    rows = json.loads(package.read(descriptor))
    expected = set(['R.images.gui.maps.icons.tankmen.icons.big.commander_friend_papacito',
                    'R.images.gui.maps.icons.tankmen.icons.big.crewSkins.commander_friend_papacito'])
    assert set(row['id'] for row in rows) == expected
    original = package.read('res/gui/maps/icons/commander_friend/profiles/papacito/portrait.jpg')
    for row in rows:
        assert row['type'] == 'Image'
        assert row['path'].startswith('img://')
        assert package.read('res/' + row['path'][6:]) == original
print('PASS: both native portrait IDs registered, paths resolve to supplied JPEG')
