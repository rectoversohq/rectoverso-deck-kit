# Versions and releases

Two things have versions: a deck, and this kit.

## A deck's versions

Every change to a deck's content is a new version, `major.minor.patch`:

| Change | Version |
|---|---|
| A fix: a typo, a wrong answer, a redrawn picture. | Patch: 1.0.0 → 1.0.1 |
| More cards, or cards retired. | Minor: 1.0.1 → 1.1.0 |
| Notes that can't carry over: their identities had to change. | Major: 1.1.0 → 2.0.0. Before 1.0, a minor. |

A release candidate is `-rc.<n>` (`1.0.0-rc.1`). The first release learners get is 1.0.0.

With every version:

- `version` and `releaseTag` move together;
- `contentModifiedAt` moves forward, never into the future. Anki updates a note only when the package's note is newer, so an edition whose time didn't move leaves a learner's deck as it was;
- `whatsNew` says what changed, in the languages the deck ships;
- `publication.release` names the new tag.

### What never changes

Once a version has been published or studied, these stay as they are, for good:

- each note's GUID;
- the ids of the note types, their fields and templates, and the Anki decks;
- each card's `card` id and each language's `book` id, where notes carry a [payload](card-payload.md);
- each language's package `id`, and the deck's `id` and `guidPrefix`.

An update recognizes the new version's notes by them and keeps the learner's progress. A note whose GUID changed is a new card beside the old one, and the progress stays with the old. So content changes freely, and identities never: a question reworded keeps its note; a retired question keeps its note too, so its history stays.

### A release

A version's release, on the deck's repository at its tag, has:

| File | What it is |
|---|---|
| `<package>.apkg`, one a language | The package, as `languages.<code>.package.file` names it. |
| `<package>.rectoverso.json`, one a language | The package's sidecar: what `inputs(language)` returns as its metadata, with the package's size and SHA-256 added under `package` (`"bytes"`, `"sha256"`). |
| The covers | Each file `covers` lists ([Covers](covers.md)). |
| `SHA256SUMS` | Every file above with its SHA-256, in `shasum -a 256`'s format: the digest, two spaces, the file name. `shasum -a 256 *.apkg *.rectoverso.json *.png > SHA256SUMS` writes it. |

A gallery that adopts the release checks every file against `SHA256SUMS`, and each package against its own sidecar. Packages are never committed to Git.

A release always has one package a language, whatever a gallery does with them afterwards. A gallery may deliver several of a deck's packages to a learner's device together (RectoVerso's does, for small decks); that grouping is the gallery's own and never appears in a deck's `rectoverso.json` or on its release.

Before a release, in this order: the deck's own checks; the kit's check; the packages opened in Anki, and an update over the previous version tried there (every review kept, no duplicate); the deck looked at in RectoVerso, in every language it ships. Then the deck's owner approves it, and `publication.approved` becomes `true`.

## The kit's versions

The kit is versioned as a whole, `major.minor.patch`, and tagged (`v1.0.0`). [CHANGELOG.md](../CHANGELOG.md) says what each version changed.

| Change to the kit | Version |
|---|---|
| A deck that passed is now refused, a field is removed, or a field's meaning changes. | Major |
| Something new a deck may use: a field, a value, a payload key. Decks that passed still pass. | Minor |
| Documentation, clearer refusals, fixes that refuse nothing new. | Patch |

A new field or value is always optional when it arrives, so a minor version never breaks a deck. The app reads what a kit version describes before that version is tagged ([CONTRIBUTING.md](../CONTRIBUTING.md)).

### Pinning the kit

A deck pins the kit as a submodule at `kit/`, at a tag. The check a deck runs is always the pinned one, so the deck's CI stays green until the deck itself moves.

### Moving to a new version

```sh
git -C kit fetch --tags
git -C kit checkout v1.1.0
python3 kit/check.py
git add kit
```

Read the changelog between the two versions, run the check, fix what it refuses (a major version says what to change), and send it as a pull request of its own. Nothing about the deck's content or identities changes by moving the kit: no new release is needed unless you adopt something new.

### A deck behind the contract

Nothing in `rectoverso.json` says which kit version a deck was written for. A gallery runs the newest kit's check on every release it adopts, so a deck behind the contract is refused there, with the rule it breaks, and is brought up to date in its own repository.
