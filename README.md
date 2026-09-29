# mulle.js

A browser port of the Swedish children's game *Mulle Meck bygger bilar* (Gary Gadget: Building Cars), written in JavaScript on top of [Phaser CE](https://github.com/photonstorm/phaser-ce). The repository also contains a small Node.js multiplayer server and Python tools for extracting graphics, sound and game data from the original Macromedia Director files.

**The game's assets are not included.** You need your own copy of the original game to extract them. Without them the client still builds and the page loads, but the game has no graphics or sound to load.

## What's in the repo

| Path | What it is |
| --- | --- |
| `src/` | Game client (ES6, bundled with webpack + Babel). `src/index.js` is the entry point, `src/scenes/` holds one file per game scene. |
| `src/index.html`, `src/style.scss` | Page shell and stylesheet for the client. |
| `data/` | Game data (cars, parts, maps, missions, worlds) already converted to JSON. Committed, so you normally don't need to regenerate it. |
| `server/server.js` | WebSocket server for the online "see other players' cars" feature. |
| `ShockwaveExtractor.py`, `ShockwaveParser.py` | Extract cast members (bitmaps, sounds, Lingo text) from Director `.DXR` / `.CXT` files. |
| `assets.py`, `audiosprite/` | Pack extracted files into Phaser texture atlases and audio sprites under `dist/assets/`. |
| `mulle.py`, `listparser.js`, `node-listparser.js` | Turn the Lingo data lists in `CDDATA.CXT` into the JSON files in `data/`. |
| `gulpfile.js`, `webpack.*.js` | Build configuration. |

## Requirements

- **Node.js.** The client bundle and the server run on current Node (tested on Node 22). The full `gulp` build needs **Node 10**, because gulp 3 and node-sass 4 do not install or run on newer versions. If you only use the manual build below, any recent Node works.
- **Python 3** with [Pillow](https://pypi.org/project/Pillow/), [PyTexturePacker](https://pypi.org/project/PyTexturePacker/) and [pydub](https://pypi.org/project/pydub/), only if you want to extract assets.
- **ffmpeg** on your `PATH`, used for converting sounds to Ogg.
- **optipng** (optional), only for the production asset build.

## Quick start (modern Node)

This builds the client without gulp, which is the easiest way to get going.

```sh
npm install --ignore-scripts          # skips node-sass, which won't compile on new Node

mkdir -p dist/data
cp src/index.html loading.png dist/
cp node_modules/phaser-ce/build/phaser.min.js dist/
cp data/*.json dist/data/
npx sass src/style.scss dist/style.css

npm start                             # webpack-dev-server on http://localhost:8080
```

`npm start` compiles `src/` into `bundle.js` in memory, serves everything else from `dist/`, and rebuilds when you edit a file. Put your extracted assets in `dist/assets/` (see below) and open <http://localhost:8080>.

## Full build with gulp (Node 10)

With Node 10 (for example via `nvm install 10 && nvm use 10`):

```sh
npm install
npx gulp              # dev build: phaser, bundle, html, css, data, assets (unoptimized)
npx gulp build-dev    # just the client, no asset extraction
npx gulp build-prod   # minified client
npx gulp build-full   # minified client + optimized assets + data
```

Everything is written to `dist/`. The `phaser` task makes a custom, smaller Phaser build with grunt. The `default` and `build-full` tasks also run `assets.py`, so they only succeed once asset extraction is set up.

After building you can serve `dist/` with `npm start`, `npm run start-prod` (production webpack settings), or any static file server.

## Getting the assets

The game data lives in Director movie and cast files on the original CD: `CDDATA.CXT`, `00.CXT` and a set of numbered `.DXR` files (`assets.py` uses `02`, `03`, `04`, `05`, `10`, `84`–`88`, `92` and `94`).

1. **Extract each file** with the Shockwave extractor:

   ```sh
   python ShockwaveExtractor.py -i /path/to/game/CDDATA.CXT -e
   python ShockwaveExtractor.py -i /path/to/game/10.DXR -e
   # ...repeat for each file listed above
   ```

   Output goes to `cst_out_new/<FILE>/<library>/<member>.png|.wav|.txt`, with a `metadata.json` per file. Other useful flags: `--fileinfo` and `--castinfo` list what a file contains, and `-m <num>` (with `-l <library>`) extracts a single member.

2. **Point `assets.py` at the extracted files.** Open `assets.py` and set `resourcePath` (currently a `<<<<<<<<<<CST STORAGE PATH>>>>>>>>>>` placeholder) to the folder that holds the `cst_out_new/*` directories. The script was written on Windows, so paths are joined with `\\`; on macOS or Linux change those to `/` (or `os.path.join`). The production build also calls `optipng.exe`, so drop the `.exe` there if needed.

3. **Build the asset packs:**

   ```sh
   python assets.py 0    # 0 = no PNG optimization; 1–7 = optipng level
   ```

   This writes texture atlases, `*-audio.ogg` sprites and a Phaser pack JSON per scene into `dist/assets/`.

### Regenerating `data/`

`data/` is already in the repo. To rebuild it from your own `CDDATA.CXT` extraction, create an empty `gamedata/` folder and run `python mulle.py`. It reads `cst_out_new/CDDATA.CXT`, parses each Lingo list through `node-listparser.js`, and writes `*.array.json` and `*.hash.json` files into `gamedata/`, which you then copy over `data/`.

## Multiplayer server

```sh
npm run server
```

This starts a WebSocket server on port **8765**. In development builds the client connects to `localhost:8765`; production builds connect to the address set in `networkServer` in `src/game.js`. The game is playable without it; it just won't show other players.

The server has a small console. Type commands into the terminal it runs in:

| Command | Effect |
| --- | --- |
| `status`, `status all`, `status world` | List connected players |
| `msg <text>` | Broadcast an admin message to connected players |
| `alert <text>` | Show a browser alert to every connected player |
| `block <map\|scene\|parts>` | Toggle relaying of that kind of update |
| `kickid <id>`, `banid <id>` | Kick or ban a player by id |
| `quit` / `exit` | Shut down |

## In the browser

The page has buttons for fullscreen, a debug toggle, and **wipe save**. Save data is stored in `localStorage` under `mulle_SaveData`.

## License

GPL-3.0. See [LICENSE](LICENSE). *Mulle Meck* and its original assets belong to their respective rights holders and are not covered by this license.
