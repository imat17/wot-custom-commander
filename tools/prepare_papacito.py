"""Convert the user-supplied clips; preserve the supplied JPEG unchanged."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import wave
import imageio_ffmpeg

root = Path(__file__).resolve().parents[1]
source = Path('C:/Users/Matisse/Downloads')
profile = root / 'assets/profiles/papacito'
voice_gain = 0.8
(profile / 'voice').mkdir(parents=True, exist_ok=True)
mapping = [
    ('papacito_start.mp3', 'start_battle', 'vo_start_battle.wav', 'Debut de bataille'),
    ('papacito_ricochet.mp3', 'enemy_ricochet_by_player', 'vo_armor_ricochet_by_player.wav', 'Ricochet de votre tir'),
    ('papacito_penetration.mp3', 'enemy_hp_damaged_by_projectile_by_player', 'vo_enemy_hp_damaged_by_projectile_by_player.wav', 'Votre tir penetrant'),
    ('papacito_dead.mp3', 'vehicle_destroyed', 'vo_vehicle_destroyed.wav', 'Votre char detruit'),
    ('papacito_destruction.mp3', 'enemy_killed_by_player', 'vo_enemy_killed_by_player.wav', 'Ennemi detruit par vous'),
    ('papacito_chenilles_fix.mp3', 'track_functional', 'vo_track_functional.wav', 'Chenilles reparees'),
    ('papacito_chenilles.mp3', 'track_destroyed', 'vo_track_destroyed.wav', 'Chenilles detruites'),
]
rows = []
for filename, event, target, label in mapping:
    src, dest = source / filename, profile / 'voice' / target
    subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), '-nostdin', '-v', 'error', '-y',
                    '-i', str(src), '-vn', '-map_metadata', '-1', '-ac', '1', '-ar',
                    '44100', '-af', 'volume=' + str(voice_gain), '-c:a', 'pcm_s16le', str(dest)], check=True)
    with wave.open(str(dest), 'rb') as wav:
        duration = wav.getnframes() / wav.getframerate()
        assert wav.getsampwidth() == 2 and wav.getnchannels() == 1
        assert 0 < duration <= 15, (filename, duration)
    rows.append(dict(source=filename, event=event, file=target, action=label,
                     seconds=round(duration, 3), source_sha256=hashlib.sha256(src.read_bytes()).hexdigest()))
shutil.copyfile(source / 'papacito-1122891.jpg', profile / 'portrait.jpg')
alias = 'vo_armor_not_pierced_by_player.wav'
shutil.copyfile(profile / 'voice/vo_armor_ricochet_by_player.wav', profile / 'voice' / alias)
next(row for row in rows if row['source'] == 'papacito_ricochet.mp3')['additional_files'] = [{
    'file': alias,
    'events': ['enemy_no_piercing_by_player', 'enemy_no_hp_damage_at_attempt_by_player',
               'frequent_enemy_no_piercing_by_player', 'frequent_enemy_no_hp_damage_at_attempt_by_player'],
    'action': 'Blindage ennemi non perce'}]
(profile / 'profile.json').write_text(json.dumps(dict(id='papacito', name='Papacito',
    portrait='portrait.jpg', voice_gain=voice_gain, recordings=rows), indent=2), encoding='utf-8')
print(json.dumps(rows, indent=2))
