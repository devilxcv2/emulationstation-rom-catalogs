# EmulationStation ROM Catalogs

Versioned JSONL game catalogs for the Android EmulationStation frontend. Each catalog can be downloaded independently from **Cataloghi online**. Game files stay on the original download services.

## On a new device

1. Open **System settings → Online catalogs**.
2. Select a system and download its catalog.
3. Choose the ROM folder and a RetroArch core or installed emulator when prompted.
4. Browse the catalog, select individual games or import the entire list.

Downloading a catalog saves it in `ROMs/lists/online/`. Importing creates link placeholders. Existing downloaded ROMs are preserved by the frontend.

## Update catalogs

Replace or add `catalogs/<system>.jsonl`, then regenerate the index:

```sh
python3 tools/build_index.py
```

Commit the catalog and `index.json` together. The index contains a content-derived version, download size, game count and SHA-256 digest for every catalog. Clients check the downloaded file before replacing their local catalog.

Run `python3 tools/validate_index.py` to verify catalogs and the index before pushing. An optional GitHub Actions template is included at `automation/update-catalogs.yml`; activate it by copying it to `.github/workflows/validate.yml` through the GitHub web interface or with credentials that include the `workflow` permission. Once activated, it regenerates the index on catalog updates and validates pull requests. When forking this repository, regenerate the index with `--base-url https://raw.githubusercontent.com/OWNER/REPOSITORY/main` and configure the resulting `index.json` URL in the app.

## Catalog format

Each line is one JSON object. Directory entries may use `type: "dir"`. Game entries use:

```json
{"type":"file","p":"Example Game.zip","n":"Example Game","ext":".zip","size":123456,"urls":[{"u":"https://example.org/games/example.zip"}]}
```

`size` is optional. The frontend shows unavailable sizes explicitly. System names come from filenames, for example `gb.jsonl` and `dreamcast.jsonl`.

## Sources

The initial catalogs were imported from the owner's local `DescargaMasiva` collection. Catalog entries and linked game files retain their original ownership and licensing terms. This repository does not grant rights to third-party games.

## Private repositories

For private repositories, set the app's index URL to `https://api.github.com/repos/OWNER/REPOSITORY/contents/index.json` and enter a GitHub token with read access to that repository in the optional token field. The app stores this token in Android private preferences and sends it only to GitHub hosts.

Generate private catalog URLs with:

```sh
python3 tools/build_index.py --base-url https://api.github.com/repos/OWNER/REPOSITORY/contents
```
