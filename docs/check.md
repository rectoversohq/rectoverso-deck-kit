# The check

The check holds a deck to [the contract](contract.md). It needs Python 3.9 or later and nothing else.

## Running it

From the deck's repository, with the kit at `kit/`:

```sh
python3 kit/check.py                # the deck in the current folder
python3 kit/check.py path/to/deck   # another one
```

It prints each language's package, then `The deck holds to the contract`, and exits 0. Or it prints `Refused:` and the first rule the deck breaks, and exits 1. It stops at the first refusal: fix it and run again.

| Option | What it does |
|---|---|
| `--rectoverso` | Also applies RectoVerso's own gallery's rules ([below](#for-rectoversos-gallery)). |
| `--python <path>` | The Python that runs the deck's `scripts/source_data.py`, when it isn't the one running the check. |
| `--version` | The kit's version. |

### What it reads

1. `rectoverso.json`, at the deck's root.
2. For each language, what `scripts/source_data.py` returns from `inputs(language)` ([Getting started](getting-started.md#4-write-scriptssource_datapy)), run in a process of its own from the deck's root.
3. The files the deck names: its tools, its source paths, its credited pictures, the sample's media.

It writes nothing, in the deck or anywhere else, and never reaches the network.

### From Python

```python
import sys
sys.path.insert(0, 'kit')
from deck_kit import check, Refusal, RECTOVERSO

try:
    artifacts = check('.')                      # or check('.', gallery=RECTOVERSO)
except Refusal as refusal:
    print(refusal)
```

`check` returns each language's expanded metadata, in the order of `languages`.

### For RectoVerso's gallery

A gallery has admission rules of its own on top of the contract. `--rectoverso` (in Python, `gallery=RECTOVERSO`) applies RectoVerso's:

- the deck's repository is `https://github.com/rectoversohq/<id>`;
- `publication.approved` is `true`;
- a Pro-only deck's repository is named `rectoverso-pro-<title>`, and no other deck's is.

Without it, the check takes a deck wherever it lives, approved or not yet. Another gallery describes its own rules with `deck_kit.Gallery(organization=…, approved_only=…, pro_prefix=…)`.

## In CI

Run the check on every pull request, with the submodule checked out. For GitHub Actions:

```yaml
name: Deck contract
on: [push, pull_request]
jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          submodules: true
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: python3 kit/check.py
```

Make it a required check on the default branch. A deck's own checks (building the packages, opening them in Anki) run beside it.

## Every refusal

Each refusal starts with the deck's id (and the language, where it is one language's), then says the rule. `…` stands for the part that names your deck's own value.

### The file itself

| Refusal | What it means | The fix |
|---|---|---|
| `no rectoverso.json at the root of the deck` | The folder checked has no `rectoverso.json`. | Run the check from the deck's root, or pass its path. |
| `rectoverso.json isn't JSON (…)` | The file doesn't parse; the message says where. | Often a trailing comma or a missing quote. |
| `rectoverso.json holds one JSON object` | The file is a list or a single value. | Wrap the fields in `{ }`. |
| `missing …` | Required fields aren't there; they are listed. | Add them ([The contract](contract.md#every-field)). |
| `rectoverso.json isn't in the contract's shape: …` | A value has the wrong type or form, in a place the rules below don't name; each is listed with where it is (`publication.remote: must match ^https://`). | Hold the file to [its schema](../schemas/rectoverso.schema.json). |

### Identity, version and publication

| Refusal | What it means | The fix |
|---|---|---|
| `repository, version, tag or publication mismatch` | One of these doesn't agree with the others: `id` and the edition expected; `releaseTag` and `v` + `version`; `publication.remote` (an `https://` address ending in the `id`); `publication.release` (the remote, `/releases/tag/`, the tag). | Make the five say the same deck and the same edition. With `--rectoverso`, the remote is under `https://github.com/rectoversohq/`. |
| `the registry only pins a tag; the deck carries its subject and covers` | A gallery passed the check more than the deck's repository and tag. | A gallery's own list names a deck and a tag, nothing else. |
| `proOnly and publication.approved are true or false` | One of the two isn't a JSON boolean. | `true` or `false`, without quotes. |
| `only an approved deck, Pro or not (proOnly), enters the catalog` | For a gallery that takes only approved decks: `publication.approved` isn't `true`. | The deck's owner approves the edition, then sets it. |
| `a Pro deck (proOnly) is private … ; every other deck is public` | `publication.visibility` doesn't match `proOnly`, or, for RectoVerso's gallery, the repository's name doesn't. | `"private"` exactly when `proOnly` is true. |
| `invalid GUID prefix or identity base` | `guidPrefix` isn't lowercase words and digits with hyphens, `identityBase` isn't an integer, or the file has a `guidForm` key. | Every deck's GUIDs have the one form: remove `guidForm`. |
| `contentModifiedAt must be an ISO 8601 time` | It doesn't parse as a time. | `2026-11-10T00:00:00Z`. |

### Words and languages

| Refusal | What it means | The fix |
|---|---|---|
| `at least one shipped language is required` | `languages` is empty, or a code isn't two lowercase letters with optional `-` parts. | `en`, `fr`, `pt-BR`. |
| `… in every shipped language is required` | `title`, `subject`, `headline` or `description` (the one named) lacks a language, has one the deck doesn't ship, or is blank in one. | One text per language in `languages`, no more, none blank. |
| `whatsNew, when given, is this version's notes in shipped languages, none empty` | `whatsNew` is empty, blank in a language, or in a language the deck doesn't ship. | Leave it out, or write it in one or more shipped languages. |
| `playLabel, when given, is the sound button's word in shipped languages, each on one line, 1 to 20 characters` | A word is too long, on two lines, has a space at an end, or is in a language the deck doesn't ship. | One short word a language. |
| `study, when given, sets one or more of …, and nothing else` | `study` has another key, a value **Deck options** doesn't offer, or is empty. | [Study options](contract.md#study-options). |
| `categories must list one or more of the contract's categories, once each` | An unknown category, one listed twice, or an empty list. | [Categories](contract.md#categories). |

### Each language's package

| Refusal | What it means | The fix |
|---|---|---|
| `the sample is missing` | The language has no `sample`, or it is blank. | Name one card ([The contract](contract.md#cards-and-languages)). |
| `invalid or duplicate artifact identity` | The language's `id` isn't lowercase words and digits with hyphens, another language has it, or the entry has a key other than `id`, `title`, `cards`, `package` and `sample`. | Five keys, an id of its own. |
| `the language's title differs from the deck's` | `languages.<code>.title` isn't `title.<code>`. | Make them the same. |
| `invalid release package name` | `package` isn't exactly `{"file": "<name>.apkg"}`, the name has a folder in it, or another language has it. | A plain file name ending in `.apkg`, different in each language. |
| `scripts/source_data.py failed: …` | `inputs(language)` raised; the last line of its error follows. | Run it yourself: `python3 -c "import sys; sys.path.insert(0, 'scripts'); from source_data import inputs; inputs('en')"`. |
| `expanded metadata differs from the declared artifact` | The first value `inputs` returns isn't `rectoverso.json` without `languages`, plus that language's `id`, `package` and `sample`, `deckID` and `language`. | Build it from the file itself, as the example does, rather than by hand. |
| `card count disagrees with the notes` | The notes don't make `cards` cards, or the language's `cards` differs from the deck's, or it isn't a whole number above 0. | A note that makes several cards says how many in its `cards`. |
| `every note GUID must be unique and start with …` | A GUID appears twice, or doesn't start with the prefix and the language. | `<guidPrefix>-<language>-<note>`. |
| `a note uses an undeclared note type` | A note's `model` isn't a key of the note types returned. | Return every note type the notes use. |
| `language note, note type or deck identities collide` | Two languages share a note GUID, a note type id or an Anki deck id, or there is no note type. | Ids of its own for each language (an offset from `identityBase` does it). |

### The sample

| Refusal | What it means | The fix |
|---|---|---|
| `the sample … is not a card of this package` | No note of this language has that GUID, or the note has no cloze of that number. | Each language names a note of its own package. |
| `the sample … can't stand alone: its note makes … cards; name one of them as …/<cloze number>` | The note makes several cards and the sample doesn't say which. | `<GUID>/<n>`. |
| `the sample … can't stand alone: its media … is missing` | A picture or sound the note's fields name isn't a file of `sourceFiles.pictures` or `sourceFiles.sounds`, or the picture has no credit. | Add the file, the folder to `sourceFiles`, and the credit. |

### Covers

| Refusal | What it means | The fix |
|---|---|---|
| `each shipped language needs one or more light and dark cover files, in order` | `covers` lacks a language, has one the deck doesn't ship, or an entry isn't exactly a non-empty `light` list and a non-empty `dark` list. | [Covers](covers.md#in-rectoversojson). |
| `a cover is listed once in its … covers` | The same file twice in one list. | Once each. |
| `… isn't a … cover's name, …` | The file isn't named as a cover is, or a cover named for dark mode is in the light list (or the other way). | [The name](covers.md#the-name). |
| `… has words in another language` | A cover named for one language is listed for another. | A cover with words is listed for its own language only. |

### Credits, licenses and files

| Refusal | What it means | The fix |
|---|---|---|
| `the deck's creator is required` | `creator` is blank. | Name who made the deck. |
| `the deck needs an open license` | `license` isn't one of the open licenses (or, for a Pro-only deck, a `LicenseRef-` identifier). | [Credits and licenses](contract.md#credits-and-licenses). |
| `at least one source is required` | `sources` is empty or isn't a list. | A deck wholly your own names itself. |
| `each source needs its name, version, license and https URL` | A source lacks one of the four, or its `url` isn't `https://`. | Fill the four. |
| `source … needs an open license (no NC or ND)` | A source's license is non-commercial or no-derivatives. | Such material can't go into an open deck. |
| `image credit count mismatch` | `pictures` isn't the number of credits, a credit has no `file`, or a picture is credited twice. | One credit a picture, and `pictures` their count. |
| `… needs an open license` | A picture's license isn't one of the open licenses. | Replace the picture, or find its real terms. |
| `missing image or credit` | A credited file isn't in the pictures folder (or, for a deck that renders its pictures, its `original` isn't in the repository), its name has a folder in it, or the credit lacks its `source` or `creator`. | Add what is missing. |
| `renderedPictures is true or false` | It isn't a JSON boolean. | `true` or `false`. |
| `sourceFiles names the paths the deck builds from` | `sourceFiles` isn't an object. | `{"pictures": "source/media", …}`. |
| `the pictures folder is missing from sourceFiles` | The deck credits pictures but names no `pictures` folder. | Add it. |
| `missing or external source path …` | A path the deck names doesn't exist, is absolute, or leaves the repository. This is also how a missing tool reads: `scripts/source_data.py`, `scripts/build.py`, `scripts/checks/validate-anki.py`, `scripts/checks/validate-rebuild.py`. | Paths are relative, inside the repository, and exist. |

### Card payloads

| Refusal | What it means | The fix |
|---|---|---|
| `…: its RectoVerso field doesn't start with a JSON object` | The note has a `RectoVerso` field that isn't empty and doesn't start with `{…}`. | Write the JSON first, escaped for HTML, and anything else after it. |
| `…: its payload isn't one the app reads: …` | A required key is missing or a known key has the wrong type or value; up to three are listed with where they are. The app would read none of the payload. | [Card payload](card-payload.md#every-key). |

### Prerequisites

| Refusal | What it means | The fix |
|---|---|---|
| `…: requires is a list of tokens, each once (lowercase words and digits, hyphens between them)` (or `introduces`) | The list isn't a list, holds something that isn't a token, or names one twice. | `["hira-3042", "hira-3044"]`. |
| `… requires …, which no card introduces` | No card of this language's package introduces that token. | Fix the token, or have the card that teaches it say so. |
| `… requires …, which only cards waiting for it introduce` | The card waits for itself, or cards wait for each other in a ring. | A card never requires what it introduces; break the ring. |
| `… requires …, which no earlier card introduces` | The card stands before the card that teaches what it requires. | Move it after, in the order `inputs` returns the notes. |
