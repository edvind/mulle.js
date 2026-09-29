// Runs a Python script with the project's .venv interpreter when there is one,
// so the npm scripts work on systems where pip can't install into the system
// Python (PEP 668). Falls back to python3 (python on Windows) on the PATH.
import { spawnSync } from 'node:child_process';
import { existsSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const windows = process.platform === 'win32';
const venvPython = path.join(root, '.venv', windows ? 'Scripts/python.exe' : 'bin/python');
const python = existsSync(venvPython) ? venvPython : windows ? 'python' : 'python3';

const result = spawnSync(python, process.argv.slice(2), { cwd: root, stdio: 'inherit' });
if (result.error) {
	console.error(`Could not run ${python}: ${result.error.message}`);
	process.exit(1);
}
process.exit(result.status ?? 1);
