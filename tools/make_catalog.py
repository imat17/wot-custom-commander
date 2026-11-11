"""Build the recording checklist from the decoded installed-client inventory."""
import collections
import hashlib
import html
import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
records = json.loads((ROOT / 'evidence/notifications.json').read_text(encoding='utf8'))
FRENCH = {
 'start_battle': 'Début de la bataille', 'respawn': 'Retour en bataille après réapparition',
 'enemy_killed': 'Destruction d’un ennemi', 'enemy_killed_by_player': 'Ennemi détruit par vous',
 'ally_killed': 'Destruction d’un allié', 'ally_killed_by_player': 'Allié détruit par vous',
 'enemy_hp_damaged_by_projectile_by_player': 'Votre projectile inflige des dégâts à l’ennemi',
 'enemy_fire_started_by_player': 'Votre tir provoque un incendie chez l’ennemi',
 'enemy_ricochet_by_player': 'Votre projectile ricoche sur l’ennemi',
 'enemy_no_piercing_by_player': 'Votre tir ne perce pas le blindage ennemi',
 'enemy_no_hp_damage_at_attempt_by_player': 'Votre tir ne retire aucun point de structure',
 'enemy_no_hp_damage_at_no_attempt_by_player': 'Impact sans dégâts aux points de structure',
 'enemy_hp_damaged_by_near_explosion_by_player': 'Explosion proche infligeant des dégâts à l’ennemi',
 'enemy_no_hp_damage_by_near_explosion_by_player': 'Explosion proche sans perte de points de structure',
 'fire_started': 'Votre char prend feu', 'fire_stopped': 'Incendie de votre char éteint',
 'vehicle_destroyed': 'Votre char est détruit', 'crew_deactivated': 'Équipage hors de combat',
 'track_functional_can_move': 'Chenilles réparées : déplacement possible',
 'target_captured': 'Cible verrouillée', 'target_lost': 'Cible perdue', 'target_unlocked': 'Verrouillage retiré',
 'ibc_ping_affirmative': 'Communication : affirmatif', 'ibc_ping_thanks': 'Communication : merci',
 'ibc_ping_help_me_ex': 'Communication : demande d’aide',
 'ibc_ping_help_me_ex_reply': 'Communication : réponse à une demande d’aide',
 'ibc_ping_retreat': 'Communication : demande de repli',
 'take_flag': 'Prise du drapeau', 'deliver_flag': 'Livraison du drapeau',
 'ally_take_flag': 'Un allié prend le drapeau', 'ally_drop_flag': 'Un allié lâche le drapeau',
 'ally_deliver_flag': 'Un allié livre le drapeau', 'enemy_take_flag': 'L’ennemi prend le drapeau',
 'observed_by_enemy': 'Détection par l’ennemi (effet sonore, pas une voix dans cette table)',
}
for part, label in {'engine':'Moteur','gun':'Canon','track':'Chenilles','turret_rotator':'Rotation de tourelle','surveying_devices':'Dispositifs d’observation','radio':'Radio','fuel_tank':'Réservoir','ammo_bay':'Râtelier de munitions'}.items():
 for suffix, state in [('damaged','endommagé(e)'),('destroyed','hors service'),('functional','réparé(e)')]:
  FRENCH[part+'_'+suffix] = label+' : '+state
for role,label in {'commander':'Chef de char','driver':'Pilote','gunner':'Tireur','loader':'Chargeur','radioman':'Opérateur radio'}.items():
 FRENCH[role+'_killed'] = label+' blessé / hors de combat'

def category(name, source):
 if source != 'gui/sound_notifications.xml': return source.split('/')[0]
 if name.startswith(('eb_', 'vo_eb_')): return 'Ligne de front'
 if name.startswith(('vo_mt_', 'mt_', 'vo_pph_', 'dc_')): return 'Entraînement / modes dédiés'
 if name.startswith('ibc_'): return 'Communications'
 if 'flag' in name: return 'Drapeaux'
 return 'Bataille / équipage'

def describe(name, source):
 base = name.replace('frequent_', '', 1)
 if base in FRENCH:
  return FRENCH[base] + (' — variante de tirs rapprochés' if name.startswith('frequent_') else '')
 for suffix, part in [('_and_chassis_damaged_by_player','chenilles'),('_and_gun_damaged_by_player','canon')]:
  if base.endswith(suffix):
   return ('Dégâts à l’ennemi et ' if base.startswith('enemy_hp_damaged') else 'Aucun dégât aux points de structure, mais ') + part + ' endommagé(es)'
 # Do not invent precise triggers from opaque or mode-specific IDs.
 return 'Événement '+category(name,source)+' : '+name+' (déclencheur précis à vérifier en jeu)'

mapping = {}
rows = []
for ordinal, record in enumerate(records):
 f=record['fields']; name=f.get('name',''); voice=f.get('infEvent','') or ''
 filename=(voice+'.wav') if voice and re.fullmatch(r'[A-Za-z0-9_]+',voice) else ''
 if filename:
  if name in mapping and mapping[name]!=filename: raise ValueError('Conflicting event '+name)
  mapping[name]=filename
 rows.append({'ordinal':ordinal,'event':name,'action':describe(name,record['source']),
  'category':category(name,record['source']),'file':filename,'source':record['source'],
  'queue':f.get('queue'), 'prototype': 'Raccordé, à tester en jeu' if filename and f.get('queue')=='1' else 'Voix non raccordée' if filename else 'Effet uniquement / aucune voix déclarée',
  'engineVoice':voice,'native':f})
out=ROOT/'dist';out.mkdir(exist_ok=True)
(ROOT/'src/custom_commander_catalog.py').write_text('# coding: utf-8\n# Generated from installed WoT EU 2.4.1.1 sound_notifications files.\nEVENT_FILES = '+repr(mapping)+'\n',encoding='utf8')
(out/'catalogue-enregistrements.json').write_text(json.dumps(rows,indent=2,ensure_ascii=False),encoding='utf8')
files=sorted(set(mapping.values()))
(out/'fichiers-a-enregistrer.txt').write_text('\n'.join(files)+'\n',encoding='utf8')
stats={'notifications':len(rows),'vocal_entries':sum(bool(r['file']) for r in rows),'unique_wav_files':len(files),'sources':sorted(set(r['source'] for r in rows))}
body=''.join('<tr><td>'+ '</td><td>'.join(html.escape(str(r[k] or '—')) for k in ['category','action','event','file','prototype','source'])+'</td></tr>' for r in rows)
page='''<!doctype html><html lang="fr"><meta charset="utf-8"><title>Custom Commander — enregistrements</title><style>body{font:16px system-ui;background:#f6f5ef;color:#202c28;margin:40px}h1{font-size:30px}p{max-width:1100px;line-height:1.6}input{padding:12px;width:70%;font:inherit;margin:20px 0}table{border-collapse:collapse;width:100%;background:white}th,td{text-align:left;padding:12px;border:1px solid #ccc;vertical-align:top;font-size:13px;overflow-wrap:anywhere}th{position:sticky;top:0;background:#173c31;color:white}tr:nth-child(even){background:#edf2ed}code{background:#e0e8e3;padding:3px}</style><h1>Custom Commander — catalogue des enregistrements</h1>'''
page+=f'<p><strong>{stats["notifications"]} entrées de notification, {stats["vocal_entries"]} entrées vocales, {len(files)} fichiers WAV distincts.</strong> Inventaire des cinq fichiers sound_notifications.xml présents dans WoT EU 2.4.1.1. Les entrées répétées du jeu sont conservées ; plusieurs actions peuvent partager un enregistrement.</p>'
starters=[('Départ','vo_start_battle.wav','En route !'),('Tir pénétrant','vo_enemy_hp_damaged_by_projectile_by_player.wav','Bien touché !'),('Ricochet','vo_armor_ricochet_by_player.wav','Ça a ricoché !'),('Ennemi détruit','vo_enemy_killed_by_player.wav','Un de moins !'),('Chenilles cassées','vo_track_destroyed.wav','On est immobilisés !'),('Chenilles réparées','vo_track_functional.wav','On peut repartir !')]
page+='<h2>Commencez avec seulement 6 enregistrements</h2><p>Tout le reste est facultatif et conserve la voix du jeu. Les 295 fichiers ci-dessous couvrent aussi des modes spéciaux : ce n’est pas une obligation par personnage.</p><table><tr><th>Situation</th><th>Fichier</th><th>Exemple libre</th></tr>'+''.join('<tr>'+''.join('<td>'+html.escape(s)+'</td>' for s in row)+'</tr>' for row in starters)+'</table><h2>Catalogue complémentaire</h2>'
page+='''<p>Un fichier par nom indiqué, WAV PCM 16 bits mono ou stéréo, de 0 à 15 secondes. Déposez vos fichiers dans <code>mods/configs/custom_commander/voice/</code>. Un fichier absent conserve la voix du jeu. Les descriptions françaises sont des explications, pas les répliques officielles à recopier.</p><p><strong>Limite de couverture :</strong> ce catalogue est complet pour ces cinq tables installées, pas pour chaque son du moteur ni chaque variante parlée des banques Wwise. Les commandes et modes spéciaux marqués à vérifier n’ont pas été validés en bataille. L’alpha remplace une annonce seulement lorsque le jeu la sélectionne dans sa file vocale et que le chef personnalisé est actif ; les replays restent inchangés.</p><label for="search">Rechercher une action, un mode ou un fichier</label><br><input id="search" type="search" placeholder="Ex. chenilles, ricochet, commander, Ligne de front…"><p id="count"></p><table><thead><tr><th>Catégorie</th><th>Action / contexte</th><th>Identifiant du jeu</th><th>Enregistrement</th><th>État du prototype</th><th>Source</th></tr></thead><tbody>'''+body+'''</tbody></table><script>const rows=[...document.querySelectorAll('tbody tr')];function filter(){const q=document.getElementById('search').value.toLocaleLowerCase('fr');let n=0;rows.forEach(r=>{r.hidden=!r.textContent.toLocaleLowerCase('fr').includes(q);if(!r.hidden)n++});document.getElementById('count').textContent=n+' entrées affichées'}document.getElementById('search').addEventListener('input',filter);filter();</script></html>'''
page=page.replace('<table><thead>', '<table id="catalogue"><thead>').replace("document.querySelectorAll('tbody tr')", "document.querySelectorAll('#catalogue tbody tr')")
(out/'Catalogue-des-enregistrements.html').write_text(page,encoding='utf8')
print(json.dumps(stats,indent=2,ensure_ascii=False))
