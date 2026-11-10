# The contract: rectoverso.json

Every deck describes itself in one file, `rectoverso.json`, at the root of its repository. It is the deck's single source of truth: its identity, its words in every language, its credits, its options. A gallery reads the deck's listing from it; the check holds it to the rules on this page.

The file is JSON. Its schema is [schemas/rectoverso.schema.json](../schemas/rectoverso.schema.json). A deck may keep keys of its own beside the ones below (a `status`, a count of sounds): the check and the app leave them aside, so a key of your own never changes what the app shows.

## An example, annotated

The [example deck's](../examples/morse-starter/rectoverso.json) file, with what each part is for. (JSON has no comments; the notes on the right are for this page only.)

```jsonc
{
  "id": "morse-starter",                    // the repository's name, stable for good
  "version": "1.0.0",                       // this edition
  "releaseTag": "v1.0.0",                   // "v" and the version: the Git tag
  "guidPrefix": "ex-morse",                 // every note's GUID starts with it
  "identityBase": 1900000000,               // the base of the deck's Anki ids
  "contentModifiedAt": "2026-11-10T00:00:00Z",   // moves forward with every content change
  "publication": {
    "remote": "https://github.com/example/morse-starter",
    "release": "https://github.com/example/morse-starter/releases/tag/v1.0.0",
    "approved": false,                      // true once this edition may be published
    "visibility": "public"
  },
  "title": {"en": "Morse starter", "fr": "Morse, premiers pas"},
  "subject": {"en": "Morse code", "fr": "Code Morse"},
  "headline": {"en": "Four letters, then the words they make.", "fr": "…"},
  "description": {"en": "Learn E, T, A and N in Morse code, …", "fr": "…"},
  "categories": ["languages"],
  "cards": 7,                               // in each language
  "pictures": 0,                            // how many pictures are credited below
  "imageCredits": [],
  "creator": "The RectoVerso deck kit's authors",
  "license": "CC-BY-4.0",
  "sources": [
    {"name": "Morse starter, the deck kit's example", "version": "1.0.0",
     "url": "https://github.com/rectoversohq/rectoverso-deck-kit", "license": "CC-BY-4.0"}
  ],
  "proOnly": false,
  "sourceFiles": {"cards": "source/cards.json", "languages": "source/languages"},
  "study": {"newCards": "deckOrder", "newPerDay": 4, "newPosition": "afterReviews"},
  "languages": {
    "en": {
      "id": "morse-starter-en",             // this language's package id, stable for good
      "title": "Morse starter",             // the same as title.en
      "cards": 7,                           // the same as cards
      "sample": "ex-morse-en-letter-e",     // the card a gallery opens as a sample
      "package": {"file": "Morse-starter-en.apkg"}
    },
    "fr": { "…": "the same five keys" }
  }
}
```

## Every field

"Required" means the check refuses a deck without it. Text is never blank.

### Identity and version

| Field | Type | Required | Rule | Why |
|---|---|---|---|---|
| `id` | text | yes | Lowercase words and digits, hyphens between them. The repository's name. | It names the deck for good: a gallery knows a deck a learner already has by it. |
| `version` | text | yes | `major.minor.patch`, with `-rc.<n>` for a release candidate (`1.0.0`, `0.3.0-rc.2`). | The app compares versions to offer an update. |
| `releaseTag` | text | yes | `v` and the version (`v1.0.0`). | It is the Git tag a gallery pins, and the release the packages are attached to. |
| `guidPrefix` | text | yes | Lowercase words and digits, hyphens between them. No `guidForm` key beside it: every deck's GUIDs have the one form. | Every note's GUID starts with it, then the language (`ex-morse-en-…`), so two decks' notes, or two languages', never collide. A deck already in a library is recognized by it. |
| `identityBase` | integer | yes | Any integer of the deck's own. | The Anki ids of the deck's note types and decks are made from it, the same at every build, so an update lands on the same note types. |
| `contentModifiedAt` | text | yes | An ISO 8601 time (`2026-11-10T00:00:00Z`). It moves forward with every change to the content, never into the future. | Anki updates a note only when the package's is newer: without it moving, a learner who has the deck keeps the old notes. |
| `publication` | object | yes | See below. | Where the deck is published, and whether this edition may be. |

`publication` has four keys, all required:

| Key | Type | Rule |
|---|---|---|
| `remote` | text | The repository's `https://` address. Its last part is the deck's `id`. |
| `release` | text | The remote, then `/releases/tag/` and the release tag. |
| `approved` | true or false | Whether the deck's owner has approved this edition for publication. The check passes either; a gallery takes only an approved one. |
| `visibility` | `"public"` or `"private"` | `"private"` exactly when `proOnly` is true. |

### Words, in every language

| Field | Type | Required | Rule | Why |
|---|---|---|---|---|
| `title` | text by language | yes | Every language in `languages`, none blank. The plain title: "Flags", "Drapeaux". | It is the deck's name in Anki and in a gallery. |
| `subject` | text by language | yes | The same. A word or two. | What the deck is about, beside its title. |
| `headline` | text by language | yes | The same. One line. | What the learner gets, at a glance. |
| `description` | text by language | yes | The same. Short. | The deck's page in a gallery. |
| `whatsNew` | text by language | no | One or more of the languages in `languages`, none blank. | This edition's notes, shown while its update waits. |
| `playLabel` | text by language | no | One or more of the languages in `languages`; each one word or so, on one line, 1 to 20 characters, no space at either end. | The word on the questions' sound button ("Listen"). Without one it says **Play**. |

[Languages](languages.md) has the rules for the words themselves.

### Cards and languages

| Field | Type | Required | Rule | Why |
|---|---|---|---|---|
| `cards` | integer | yes | 1 or more. Each language's notes make exactly this many cards. | A gallery says how many before the deck is added. |
| `languages` | object by language code | yes | One or more. A code is two lowercase letters, with optional `-` parts (`en`, `fr`, `pt-BR`). | Each language is a package of its own, with ids of its own: adding French never touches English's progress. |

Each language has exactly these five keys:

| Key | Type | Rule |
|---|---|---|
| `id` | text | Lowercase words and digits, hyphens between them; no other language of the deck has it. Stable for good. |
| `title` | text | The same as `title` in that language. |
| `cards` | integer | The same as `cards`. |
| `sample` | text | The one card a gallery opens as a sample question, before the deck is added. A note that makes one card is named by its GUID; one card of a note that makes several (a cloze of several blanks, an image occlusion of several labels) by `<GUID>/<n>`, n its cloze number. Every picture or sound the sample's fields name is one of the deck's source files. |
| `package` | object | Exactly `{"file": "<name>.apkg"}`: the package's file name on the release, with no folder, different in each language. |

The notes themselves have rules too, which the check holds through `scripts/source_data.py` ([Getting started](getting-started.md#4-write-scriptssource_datapy)):

- **Every GUID** is unique, and starts with the prefix and the language: `<guidPrefix>-<language>-`.
- **The notes make exactly `cards` cards:** a note counts as one unless it says how many in `cards`.
- **Note types and Anki decks** have ids no other language of the deck uses.
- **A note's payload,** when it has one, is one the app reads ([Card payload](card-payload.md)), and what cards require and introduce holds together ([Prerequisites](prerequisites.md)).

### Study options

| Field | Type | Required | Rule | Why |
|---|---|---|---|---|
| `study` | object | no | One or more of the three keys below, and no other. | A course whose cards build on each other needs its order from the first day, before a learner would think to open **Deck options**. |

| Key | Values | The app's default |
|---|---|---|
| `newCards` | `"random"` or `"deckOrder"` | `"random"` |
| `newPerDay` | An integer from 1 to 999 | 20 |
| `newPosition` | `"afterReviews"`, `"beforeReviews"` or `"mixed"` | `"afterReviews"` |

A deck added from a gallery comes into the library with them, and the learner changes them as any deck's. A deck opened as a file comes in with the app's defaults: the options travel in a gallery's listing, not in the package. Whatever the options, [prerequisites](prerequisites.md) travel in the package and hold the order that matters.

### Categories

| Field | Type | Required | Rule | Why |
|---|---|---|---|---|
| `categories` | list | yes | One or more of the categories below, each once. | The first places the deck in a gallery's sections; the others help search and filters. |

| Category | English | French |
|---|---|---|
| `geography` | Geography | Géographie |
| `history` | History | Histoire |
| `languages` | Languages | Langues |
| `sciences` | Sciences | Sciences |
| `mathematics` | Mathematics | Mathématiques |
| `medicine` | Medicine | Médecine |
| `arts` | Arts | Arts |
| `music` | Music | Musique |

### Credits and licenses

| Field | Type | Required | Rule | Why |
|---|---|---|---|---|
| `creator` | text | yes | Who made the deck. | Shown with the deck. |
| `license` | text | yes | One of `CC0-1.0`, `CC-BY-4.0`, `CC-BY-SA-4.0`, `MIT`, `Apache-2.0`, `Public domain`. A Pro-only deck may instead name its own terms, `LicenseRef-<name>`. | A public deck is open: learners may keep, change and share it. |
| `sources` | list | yes | One or more. Each has a `name`, a `version`, an `https://` `url` and a `license`, none blank. A source's license is never non-commercial (NC) or no-derivatives (ND). | A deck made from another says where it comes from, at which version, under which terms. A deck wholly your own names itself. |
| `pictures` | integer | yes | How many pictures the deck credits: the length of `imageCredits`. | A count a gallery can show, held to the credits. |
| `imageCredits` | list | yes | One credit per picture, each picture once. Empty for a deck without pictures. | Every picture has its author and its terms. |
| `renderedPictures` | true or false | no | `true` for a deck whose build renders its pictures from vector originals, so the rendered files stay out of Git. | Each credit then names its `original` instead of a file in the pictures folder. |

Each credit has:

| Key | Type | Required | Rule |
|---|---|---|---|
| `file` | text | yes | The picture's file name, with no folder. It is a file of the pictures folder (`sourceFiles.pictures`), unless the deck renders its pictures. |
| `source` | text | yes | Where it comes from: an address or a description. |
| `creator` | text | yes | Its author. |
| `license` | text | yes | One of the open licenses listed for `license` above. |
| `original` | text | only with `renderedPictures` | The file in the repository the picture is rendered from. |

### Files

| Field | Type | Required | Rule | Why |
|---|---|---|---|---|
| `sourceFiles` | object | yes | Each value is a path inside the repository that exists. `pictures` is the folder the credited pictures are in (required as soon as there is a credit, unless the deck renders its pictures); `sounds` is the folder of the sounds. Other keys are the deck's own. | The check finds the sample's media and the credited pictures there. |
| `covers` | object by language | no | See [Covers](covers.md). | The pictures a gallery shows of the deck. |

### Pro

| Field | Type | Required | Rule | Why |
|---|---|---|---|---|
| `proOnly` | true or false | yes | `true` only for a deck offered with RectoVerso Pro alone, from a private repository. | The app adds and opens such a deck only with Pro, and never exports it. Every other deck is public and open. |

## What a gallery adds

The contract above is the same for every deck. A gallery adds its own admission rules, which the check applies when asked ([The check](check.md#for-rectoversos-gallery)). RectoVerso's own:

- The deck's repository is in the `rectoversohq` organization on GitHub, so `publication.remote` is `https://github.com/rectoversohq/<id>`.
- `publication.approved` is `true`.
- A Pro-only deck's repository is named `rectoverso-pro-<title>`, and no other deck's is.
