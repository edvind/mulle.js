# mulle.js

A browser port of the Swedish children's game *Mulle Meck bygger bilar* (Gary Gadget: Building Cars), written in JavaScript on top of [Phaser CE](https://github.com/photonstorm/phaser-ce). The repository also contains a small Node.js multiplayer server and Python tools for extracting graphics, sound and game data from the original Macromedia Director files.

**The game's assets are not included.** You need your own copy of the original game to extract them. Without them the client still builds and the page loads, but the game has no graphics or sound to load.

## What's in the repo

| Path | What it is |
| --- | --- |
| `src/` | Game client (ES modules, bundled with Vite). `src/index.js` is the entry point, `src/scenes/` holds one file per game scene. |
| `src/index.html`, `src/style.scss` | Page shell and stylesheet for the client. |
| `data/` | Game data (cars, parts, maps, missions, worlds) already converted to JSON. Committed, so you normally don't need to regenerate it. |
| `server/server.js` | WebSocket server for the online "see other players' cars" feature. |
| `ShockwaveExtractor.py`, `ShockwaveParser.py` | Extract cast members (bitmaps, sounds, Lingo text) from Director `.DXR` / `.CXT` files. |
| `assets.py`, `audiosprite/` | Pack extracted files into Phaser texture atlases and audio sprites under `dist/assets/`. |
| `mulle.py`, `listparser.js`, `node-listparser.js` | Turn the Lingo data lists in `CDDATA.CXT` into the JSON files in `data/`. |
| `vite.config.mjs` | Build and dev server configuration. |

## Requirements

- **Node.js 22 or newer.**
- **Python 3** with the packages in `requirements.txt`, only if you want to extract assets.
- **ffmpeg** on your `PATH`, used for converting sounds to Ogg.
- **optipng** (optional), only for the production asset build.

## Building and running

```sh
npm install
npm run dev        # dev server with live reload on http://localhost:8080
npm run build      # production build into dist/
npm run preview    # serve the production build on http://localhost:8080
```

Put your extracted assets in `dist/assets/` (see below). The dev server serves them from there, along with Phaser (the prebuilt arcade-physics bundle from `phaser-ce`), `data/` and `loading.png`. `npm run build` writes the page, the bundle (under `dist/build/`), Phaser and `data/` into `dist/`, and leaves `dist/assets/` alone, so you can host `dist/` with any static file server.

Production builds strip `console.debug` calls and connect to the multiplayer server set in `networkServer` in `src/game.js`; dev builds connect to `localhost:8765`.

The optional custom cursors are loaded from `dist/ui/*.png`. Vite warns that it can't resolve them at build time; that's expected, since they aren't in the repo.

## Getting the assets

You need your own copy of the original game, either as an ISO image or as a folder (for example the mounted CD). With that, one command installs everything:

```sh
python3 -m venv .venv && . .venv/bin/activate
python3 -m pip install -r requirements.txt
npm run install-assets -- /path/to/mulle.iso      # or a folder with the game files
```

`install_assets.py` finds the Director files the port uses (`CDDATA.CXT`, `00.CXT` and `02`, `03`, `04`, `05`, `10`, `84`–`88`, `92` and `94.DXR`), copies them to `game/files/`, extracts their cast members into `cst_out_new/` and packs texture atlases, `*-audio.ogg` sprites and a Phaser pack JSON per scene into `dist/assets/`. Add `--optimize 1`–`7` to shrink the atlases with optipng. `game/`, `cst_out_new/`, `dist/` and game files are gitignored; never commit them.

### Doing it step by step

1. **Extract each file** with the Shockwave extractor:

   ```sh
   python3 ShockwaveExtractor.py -i /path/to/game/CDDATA.CXT -e
   python3 ShockwaveExtractor.py -i /path/to/game/10.DXR -e
   # ...repeat for each file listed above
   ```

   Output goes to `cst_out_new/<FILE>/<library>/<member>.png|.wav|.txt`, with a `metadata.json` per file. Other useful flags: `--fileinfo` and `--castinfo` list what a file contains, and `-m <num>` (with `-l <library>`) extracts a single member.

2. **Build the asset packs:**

   ```sh
   mkdir -p dist/assets
   npm run assets        # same as: python3 assets.py 0 (no PNG optimization)
   npm run assets-prod   # same as: python3 assets.py 7 (optipng level 7)
   ```

   `assets.py` reads from `cst_out_new/`; set `MULLE_CST_PATH` to use another folder.

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
