# Getting started

From an empty repository to a deck that passes the check. The [example deck](../examples/morse-starter) is the result of these steps: read it alongside.

You need Git and Python 3.9 or later. The check itself installs nothing. Building a package needs Anki's Python library (`pip install anki`), which only your own build script uses.

## 1. Lay the repository out

One repository holds one deck, in every language it ships. Every deck has the same few fixed places, so the check, and anyone who opens the repository, knows where to look:

```
your-deck/
  rectoverso.json            the deck's description of itself
  kit/                       this kit, a Git submodule
  source/                    your content: cards, translations, pictures, sounds
  scripts/
    source_data.py           says what each language's notes are
    build.py                 builds one language's package
    checks/
      validate-anki.py       opens a built package in Anki
      validate-rebuild.py    holds a second build to the first
  README.md, LICENSE
```

How you arrange `source/` is yours. Packages (`.apkg`), rendered pictures and build output stay out of Git: a package goes on the deck's release.

Add the kit, pinned to a version:

```sh
git submodule add https://github.com/rectoversohq/rectoverso-deck-kit.git kit
git -C kit checkout v1.0.0
git add .gitmodules kit
```

## 2. Decide what never changes

A learner's progress follows identities. Choose them once; a deck that has been studied never changes them ([Versioning](versioning.md#what-never-changes)).

- **The deck's id:** its repository's name, in lowercase words and hyphens (`morse-starter`).
- **A GUID prefix:** short, lowercase, yours alone (`ex-morse`). Every note's GUID is the prefix, the language, then the note: `ex-morse-en-letter-e`.
- **An identity base:** a large integer of your own. The Anki ids of your note types and decks are made from it, the same at every build.
- **Each language's package id:** `morse-starter-en`, `morse-starter-fr`.

## 3. Write rectoverso.json

Start from the [example's](../examples/morse-starter/rectoverso.json) and change every value. [The contract](contract.md) explains each field. While you work, `publication.approved` is `false`: the check passes a deck that isn't approved yet, and a gallery takes it only once it is.

Your editor can hold the file to its schema as you type. In VS Code, for instance:

```json
{ "json.schemas": [{ "fileMatch": ["rectoverso.json"], "url": "./kit/schemas/rectoverso.schema.json" }] }
```

## 4. Write scripts/source_data.py

The check never reads your `source/` folder itself. It asks your `scripts/source_data.py`, in a process of its own, with nothing installed:

```python
def inputs(language):
    ...
    return expanded, notes, types, deck
```

All four are plain JSON values.

| Returned | What it is |
|---|---|
| `expanded` | The language's metadata: `rectoverso.json` without `languages`, plus `id`, `package` and `sample` from that language's entry, `deckID` (the deck's id) and `language` (its code). The check holds it to exactly that. |
| `notes` | The language's notes, in the order the deck is studied. Each has a `guid`, a `model` (the name of its note type), and its `fields` by name. A note that makes several cards (a cloze of several blanks, an image occlusion of several labels) says how many in `cards`. |
| `types` | The note types, by the name the notes use, each with an `id` no other language of the deck uses. |
| `deck` | The Anki deck the notes go in: its `id`, different in each language, and its `name`. |

Your build script uses the same function, so what the check reads is what the package holds. The example's [source_data.py](../examples/morse-starter/scripts/source_data.py) is sixty lines.

To tell RectoVerso more about a card than Anki's fields can, give its note a field named `RectoVerso` holding a small JSON object, the card's [payload](card-payload.md). That is where a card says what it [builds on](prerequisites.md).

## 5. Build and look

Three more scripts are yours to write; the check only holds that they exist where every deck's are.

- `scripts/build.py --language <code> --out <package>` builds one language's package and writes its sidecar beside it ([Versioning](versioning.md#a-release)).
- `scripts/checks/validate-anki.py <package>` opens the package in Anki and holds it to the source.
- `scripts/checks/validate-rebuild.py <first> <second>` holds a second build to the first: same notes, same identities.

The example's three use Anki's Python library and are short enough to copy. Then look at the deck yourself: open the package in Anki, and in RectoVerso on an iPhone (**Import Anki deck…**). No check stands in for that.

## 6. Run the check

```sh
python3 kit/check.py
```

It prints each language's package and "The deck holds to the contract", or the first rule the deck breaks. [The check](check.md) lists every refusal, what it means and how to fix it.

## 7. Check every change

Run the check in your repository's CI, so a change that breaks the contract never merges ([The check in CI](check.md#in-ci)).

## What next

- [Prerequisites](prerequisites.md), if some of your cards build on others.
- [Covers](covers.md), if the deck is to be shown in a gallery.
- [Languages](languages.md), before you add a second language.
- [Versioning](versioning.md), before your first release.
