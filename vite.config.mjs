import { defineConfig } from 'vite';
import { createReadStream, existsSync, readdirSync, rmSync, statSync } from 'node:fs';
import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.dirname(fileURLToPath(import.meta.url));
const src = path.join(root, 'src');
const dist = path.join(root, 'dist');
const phaserDir = path.join(root, 'node_modules/phaser-ce/build/custom');

// Files that aren't part of the JS bundle but are loaded by the game at runtime.
// Keys are URL paths, values are files or folders on disk.
const staticFiles = {
	'phaser-arcade-physics.min.js': path.join(phaserDir, 'phaser-arcade-physics.min.js'),
	'phaser-arcade-physics.map': path.join(phaserDir, 'phaser-arcade-physics.map'),
	'loading.png': path.join(root, 'loading.png'),
	'data': path.join(root, 'data'),
};

const mimeTypes = {
	'.js': 'text/javascript',
	'.json': 'application/json',
	'.map': 'application/json',
	'.png': 'image/png',
	'.jpg': 'image/jpeg',
	'.ogg': 'audio/ogg',
	'.mp3': 'audio/mpeg',
	'.wav': 'audio/wav',
};

function listFiles(dir) {
	return readdirSync(dir, { withFileTypes: true }).flatMap((entry) => {
		const full = path.join(dir, entry.name);
		return entry.isDirectory() ? listFiles(full) : [full];
	});
}

// Generated locally by assets.py (and cursor images copied by hand). Served from
// dist/ during development; a build leaves them where they are.
const generatedFiles = {
	'assets': path.join(dist, 'assets'),
	'ui': path.join(dist, 'ui'),
};

function resolveStatic(urlPath) {
	for (const [name, target] of Object.entries({ ...staticFiles, ...generatedFiles })) {
		if (urlPath === name) return target;
		if (urlPath.startsWith(name + '/')) {
			const file = path.join(target, urlPath.slice(name.length + 1));
			return file.startsWith(target + path.sep) ? file : null;
		}
	}
	return null;
}

function sendFile(res, file) {
	res.setHeader('Content-Type', mimeTypes[path.extname(file)] || 'application/octet-stream');
	createReadStream(file).pipe(res);
}

function isFile(file) {
	return file && existsSync(file) && statSync(file).isFile();
}

/**
 * Serves Phaser, game data and extracted assets during development, and copies
 * Phaser and game data into dist/ on build. Extracted assets are generated into
 * dist/assets by assets.py and are never part of the repository.
 */
function mulleStatic() {
	let isBuild = false;
	return {
		name: 'mulle-static',
		configResolved(config) {
			isBuild = config.command === 'build';
		},
		buildStart() {
			// dist/ can't be emptied (see build.emptyOutDir), so clear out old bundles here.
			if (isBuild) rmSync(path.join(dist, 'build'), { recursive: true, force: true });
		},
		configureServer(server) {
			server.middlewares.use((req, res, next) => {
				const urlPath = decodeURIComponent(new URL(req.url, 'http://localhost').pathname).replace(/^\/+/, '');
				const file = resolveStatic(urlPath);
				if (isFile(file)) return sendFile(res, file);
				next();
			});
		},
		async generateBundle() {
			for (const [name, target] of Object.entries(staticFiles)) {
				const files = statSync(target).isDirectory() ? listFiles(target) : [target];
				for (const file of files) {
					const fileName = statSync(target).isDirectory()
						? path.posix.join(name, path.relative(target, file).split(path.sep).join('/'))
						: name;
					this.emitFile({ type: 'asset', fileName, source: await readFile(file) });
				}
			}
		},
	};
}

export default defineConfig({
	root: src,
	base: './',
	publicDir: false,
	resolve: {
		// The game imports its own modules by bare path, e.g. `import MulleSprite from 'objects/sprite'`.
		alias: [
			{ find: /^(objects|scenes|struct|util)\/(.*)$/, replacement: path.join(src, '$1/$2') },
			{ find: /^(game|load|boot)$/, replacement: path.join(src, '$1.js') },
		],
	},
	plugins: [mulleStatic()],
	server: {
		port: 8080,
	},
	preview: {
		port: 8080,
	},
	build: {
		outDir: dist,
		// dist/assets holds extracted game assets, so never wipe dist/.
		emptyOutDir: false,
		// Keep bundle output apart from the extracted assets in dist/assets.
		assetsDir: 'build',
		sourcemap: true,
		rolldownOptions: {
			// Strip debug logging from production bundles.
			treeshake: { manualPureFunctions: ['console.debug'] },
		},
	},
});
