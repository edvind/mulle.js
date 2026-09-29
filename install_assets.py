#!/usr/bin/env python3
"""
Install the game assets from your own copy of the original game.

    python3 install_assets.py /path/to/mulle.iso
    python3 install_assets.py /path/to/mounted/cd

Finds the Director files the port needs on the disc image (or in a folder),
copies them to game/files/, extracts their cast members into cst_out_new/
with ShockwaveExtractor.py, and packs them into dist/assets/ with assets.py.
game/, cst_out_new/ and dist/ are all gitignored: never commit what this
script produces.
"""

import argparse
import importlib
import os
import shutil
import subprocess
import sys
import warnings

ROOT = os.path.dirname(os.path.abspath(__file__))

# Every Director file that assets.py reads from.
REQUIRED_FILES = [
	'00.CXT', 'CDDATA.CXT',
	'02.DXR', '03.DXR', '04.DXR', '05.DXR', '10.DXR',
	'84.DXR', '85.DXR', '86.DXR', '87.DXR', '88.DXR', '92.DXR', '94.DXR',
]

# Module to import -> package that provides it. aifc, sunau and pydub's audioop
# left the standard library in Python 3.13 and come from backports there.
PYTHON_MODULES = {
	'PIL': 'Pillow',
	'PyTexturePacker': 'PyTexturePacker',
	'pydub': 'pydub (and audioop-lts on Python 3.13+)',
	'aifc': 'standard-aifc',
	'sunau': 'standard-sunau',
	'bitstring': 'bitstring',
	'pycdlib': 'pycdlib',
}


def fail(message):
	print('error: ' + message, file=sys.stderr, flush=True)
	sys.exit(1)


def check_requirements(optimize):
	missing = []
	for module, package in PYTHON_MODULES.items():
		try:
			with warnings.catch_warnings():
				# pydub warns about ffmpeg on import; that's checked below.
				warnings.simplefilter('ignore')
				importlib.import_module(module)
		except ImportError:
			missing.append(package)
	if missing:
		fail('missing Python packages: ' + ', '.join(missing) + '\n'
			'Install them into a virtualenv, which the npm scripts use automatically:\n'
			'  python3 -m venv .venv && .venv/bin/python -m pip install -r requirements.txt')
	if not shutil.which('ffmpeg'):
		fail('ffmpeg was not found on your PATH. It is needed to convert the game sounds.')
	if optimize > 0 and not shutil.which('optipng'):
		fail('optipng was not found on your PATH. Install it or use --optimize 0.')


def plain_name(name):
	"""ISO 9660 names can carry a ';1' version suffix."""
	return name.split(';')[0].rstrip('.').upper()


def copy_from_folder(source, dest):
	found = {}
	for dirpath, _, filenames in os.walk(source):
		for name in filenames:
			key = plain_name(name)
			if key in REQUIRED_FILES and key not in found:
				found[key] = os.path.join(dirpath, name)
	for key, path in found.items():
		shutil.copyfile(path, os.path.join(dest, key))
	return set(found)


def copy_from_iso(source, dest):
	import pycdlib

	iso = pycdlib.PyCdlib()
	try:
		iso.open(source)
	except Exception as e:
		fail('could not read %s as an ISO image: %s' % (source, e))

	# Prefer the long-name directory trees when the disc has them.
	if iso.has_rock_ridge():
		key_name = 'rr_path'
	elif iso.has_joliet():
		key_name = 'joliet_path'
	else:
		key_name = 'iso_path'

	found = {}
	try:
		for dirpath, _, filenames in iso.walk(**{key_name: '/'}):
			for name in filenames:
				key = plain_name(name)
				if key in REQUIRED_FILES and key not in found:
					found[key] = dirpath.rstrip('/') + '/' + name
		for key, path in found.items():
			iso.get_file_from_iso(os.path.join(dest, key), **{key_name: path})
	finally:
		iso.close()
	return set(found)


def run(args):
	print('$ ' + ' '.join(args), flush=True)
	env = dict(os.environ, MULLE_CST_PATH=os.path.join(ROOT, 'cst_out_new'), PYTHONUNBUFFERED='1')
	result = subprocess.run(args, cwd=ROOT, env=env)
	if result.returncode != 0:
		fail('%s exited with status %d' % (os.path.basename(args[1]), result.returncode))


def main():
	parser = argparse.ArgumentParser(description='Install game assets from an ISO image or a folder with the game files.')
	parser.add_argument('source', help='path to the game ISO, or to a folder such as the mounted CD')
	parser.add_argument('--optimize', type=int, default=0, choices=range(0, 8), metavar='0-7',
		help='optipng level for the texture atlases (default 0, no optimization)')
	args = parser.parse_args()

	source = os.path.abspath(args.source)
	if not os.path.exists(source):
		fail('%s does not exist' % source)

	check_requirements(args.optimize)

	game_dir = os.path.join(ROOT, 'game', 'files')
	os.makedirs(game_dir, exist_ok=True)

	print('Copying game files from ' + source, flush=True)
	if os.path.isdir(source):
		found = copy_from_folder(source, game_dir)
	else:
		found = copy_from_iso(source, game_dir)

	missing = [f for f in REQUIRED_FILES if f not in found]
	if missing:
		fail('these files were not found in %s: %s' % (source, ', '.join(missing)))

	# Start from a clean extraction so stale files from an earlier run can't sneak in.
	shutil.rmtree(os.path.join(ROOT, 'cst_out_new'), ignore_errors=True)
	for name in REQUIRED_FILES:
		run([sys.executable, 'ShockwaveExtractor.py', '-i', os.path.join(game_dir, name), '-e'])

	os.makedirs(os.path.join(ROOT, 'dist', 'assets'), exist_ok=True)
	run([sys.executable, 'assets.py', str(args.optimize)])

	print('', flush=True)
	print('Assets installed in dist/assets. Start the game with: npm run dev', flush=True)


if __name__ == '__main__':
	main()
