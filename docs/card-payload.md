# What a note tells the app

RectoVerso opens any Anki package and makes cards of its notes by itself: a deck of plain Anki notes works. This page is about what a deck can add, so the app knows what Anki has no field for.

- **The payload:** a small JSON object in a note field named `RectoVerso`. It gives the card an identity of its own, says how its answer is revealed, and carries what the card [builds on](prerequisites.md). Most of this page.
- **Three other fields** the app reads by name: [`RectoVerso search`](#rectoverso-search), [`RectoVerso place`](#rectoverso-place) and [`RectoVerso Occlusion`](#rectoverso-occlusion).

None of these fields is shown by Anki unless a template names it, so a deck studies in Anki exactly as it did.

## The payload

### Where it goes

Add a field named exactly `RectoVerso` to the note type, and name it in no template. Its text starts with the JSON object. A field is HTML to Anki, so the JSON is escaped in it (`"` written as `&quot;`); in Python, `html.escape(json.dumps(payload))`.

The app reads the object the field starts with, through its closing brace, and leaves aside whatever follows. A deck may put references to extra media after it (`<img src="…">`), so Anki packs files that only the app shows.

### An example, annotated

The payload of the word TEA in the [example deck](../examples/morse-starter):

```jsonc
{
  "v": 1,                                             // the payload's version
  "book": "6ffcc562-529a-5939-b5bf-1900566aac55",     // the deck's id in the app's library
  "card": "b626352e-ba84-5aac-b320-9b9b897c919b",     // the card's own id
  "kind": "basic",                                    // how the answer is revealed
  "noteID": "ex-morse-en-word-tea",                   // what its siblings would share
  "requires": ["a", "e", "t"]                         // what the card builds on
}
```

### Every key

Four keys are required. A payload without one of them, or with a known key of the wrong type, can't be read at all: the app then makes the card as it would an ordinary Anki note, without the identity the payload gave it. That is why the check refuses such a payload ([schemas/card-payload.schema.json](../schemas/card-payload.schema.json)). A key the app doesn't know is ignored.

| Key | Type | Required | Rule | What the app does with it |
|---|---|---|---|---|
| `v` | integer | yes | `1`. | The payload's version. A later version this app can't read is left aside. |
| `book` | text | yes | A UUID (`6ffcc562-529a-5939-b5bf-1900566aac55`), the same for every card of one language's package, different in each language, stable for good. | The deck's id in the learner's library. All the notes of one Anki deck carry the same one; an update lands on the deck the learner has. |
| `card` | text | yes | A UUID, the card's own, stable for good. | The card's id: the learner's progress is kept by it. |
| `kind` | text | yes | `"basic"`, `"cloze"`, `"definition"` or `"occlusion"`. | How the answer comes out: letter by letter or as a picture uncovered (`basic`); a blank in a sentence (`cloze`); prose that sharpens from a blur (`definition`); a covered label of a figure (`occlusion`). |
| `noteID` | text | no | Any text; usually the note's GUID. | Cards with the same `noteID` are siblings: the app shows one of them a day. Cards that shouldn't hold each other back each have their own. |
| `requires` | list of text | no | Tokens, each once: lowercase words and digits, hyphens between them. Each is introduced by another card of the same package. | What the card builds on ([Prerequisites](prerequisites.md)). |
| `introduces` | list of text | no | Tokens, each once, in the same form. | What the card teaches. |
| `resources` | list | no | Each item has a `name` and a `text` (both text), and optionally `images` (media file names). | Extra lines under the answer once it is whole, each under its name (a reading in romaji, a mnemonic). |
| `otherText` | text | no | | A title for the card in lists, for a card whose question and answer are both pictures. |
| `otherTextSource` | text | no | The name of the field `otherText` comes from. | A title from a field named Title, Caption, Name or Description is also searchable. |
| `occlusion` | object | no | See [A figure's card](#a-figures-card). | The figure and what is covered on it, for a card of kind `occlusion`. |
| `preparation` | object | no | See [A prepared figure](#a-prepared-figure). | Reviewed, clean pictures and regions for a figure. |
| `originalOcclusionAnswer` | text | no | The answer as the deck wrote it. | Lets the app tell a later edit of the Back field, made in Anki, from the deck's own answer. |
| `place` | object | no | See [A place](#a-place). | The place the card asks for, drawn on a live map. |

Three more keys, `memory`, `lastReview` and `reviews`, are written by the app's own export for Anki: a learner's progress on its way through Anki and back. A deck leaves them out.

### The words come from the visible fields

The payload holds no text of the card. The app reads the question and the answer from the note's visible fields, by name, so a note edited in Anki keeps its edits:

| Note type | Fields the app reads |
|---|---|
| An ordinary one | `Front` (the question, its first picture and its sounds), `Back` (the answer, an answer picture, sounds), and as plain text `Kicker` (the small line that says what kind of question this is), `Meta`, `Example` and `Note`. |
| A cloze one | `Text` (its first cloze, `{{c1::answer}}`, becomes the blank and the answer), `Back Extra` (the example, an answer picture, sounds), and as plain text `Kicker`, `Meta` and `Note`. |

A question that is only a sound, with nothing else in `Front`, is a listening card: the app plays it as the card appears.

### How identities are kept

- **The deck:** an Anki deck whose notes all carry the same `book` becomes that deck in the library. If an Anki deck mixes several `book` values, or mixes notes with and without a payload, the app can't tell whose it is and gives it an id of its own.
- **The card:** a card keeps its `card` id when its Anki deck is the deck its `book` names. Otherwise it gets an id made from its note's GUID.
- **So:** one Anki deck per language, every note of it with the same `book`, every card with its own `card`, none of them ever changed. A deterministic UUID does it, as the example's `uuid.uuid5` of the note's GUID.

### A figure's card

For a card of kind `occlusion`. Positions are fractions of the picture, from its top-left corner (0 to 1).

| Key | Type | Required | Rule |
|---|---|---|---|
| `imageName` | text | yes | The figure's media file name. |
| `box` | rect | yes | The bounds of what the card asks: `[[x, y], [width, height]]`. |
| `shapes` | list of shapes | no | What the card covers and asks. |
| `siblings` | list of shapes | no | The figure's other covered shapes. |
| `label` | text | no | The answer under the cover, when it is text. |
| `mode` | text | no | `"hideAll"`: the figure's other labels stay covered while this one is asked. `"hideOne"`: they show. |
| `ordinal` | integer | no | The card's number within its figure, from 1. |
| `imageSize` | list | no | The figure's size in pixels: `[width, height]`. |
| `labelAnswers`, `texts`, `detailsAfterAnswer`, `lit`, `position` | | no | Set by the app as it reads a figure; a deck leaves them out, and `preparationID` too. |

A shape is an object with exactly one key, in the form the app's own export writes:

```json
{"rect": {"_0": [[0.12, 0.30], [0.20, 0.08]]}}
{"ellipse": {"_0": [[0.12, 0.30], [0.20, 0.08]]}}
{"polygon": {"_0": [[0.10, 0.10], [0.40, 0.12], [0.25, 0.35]]}}
```

A rect and an ellipse are a box, `[[x, y], [width, height]]`, the ellipse inscribed in it; a polygon is its corners.

### A prepared figure

A deck that has reviewed its figures can ship them prepared: for each figure, the original picture, a clean one with its labels removed, and the regions of its labels. The app then shows a covered label with nothing of it leaking through. It validates a preparation at import (each file present, with the size and the SHA-256 it declares); one that fails leaves the ordinary occlusion card.

| Key | Type | Required | Rule |
|---|---|---|---|
| `version` | integer | yes | `1`. |
| `source`, `clean` | asset | yes | The original picture and the clean one, the same size. |
| `darkSource`, `darkClean` | asset | no | A pair for dark mode: both or neither, the same size as `source`. |
| `masksSHA256` | text | yes | The SHA-256 of the note's `Occlusion` field (Anki's own masks), 64 lowercase hexadecimal digits. |
| `mode` | text | yes | `"hideAll"`, `"hideOne"` or `"lit"` (the whole figure shown, the card's region outlined, its name asked). |
| `regions` | list | yes | 1 to 1,024 regions, their shapes all different. |
| `canvas` | object | no | The figure's background: `{"method": "flat-srgb-v1", "light": [r, g, b]}`, each from 0 to 1, with `"dark"` exactly when there is a dark pair. |

An asset is `{"file": …, "sha256": …, "width": …, "height": …}`: a media file name (no folder, not starting with a dot), its SHA-256, and its size in pixels (1 to 16,384 a side).

A region:

| Key | Type | Required | Rule |
|---|---|---|---|
| `id` | text | yes | Its own within the figure, up to 128 characters. |
| `ordinal` | integer | yes | The card of the figure it belongs to, 1 to 1,024. In `lit` mode, each region has its own. |
| `kind` | text | yes | `"label"` (a printed label) or `"picture"` (a part of the picture). |
| `geometry` | object | yes | `{"kind": "rect" \| "ellipse" \| "polygon", "coordinates": […]}`: `[x, y, width, height]` for a rect or an ellipse, inside the picture; x, y pairs for a polygon of 3 to 256 corners. Fractions of the picture from its top-left corner. |
| `answer` | text | no | The exact answer, up to 512 characters. Never on a `picture` region. |
| `title`, `detail` | text | no | Up to 256 and 1,024 characters, shown once the answer is whole. In `lit` mode `title` is required: it is the answer. |
| `position` | text | no | The region's place in the figure's own words ("period 4, group 8"), up to 128 characters, which VoiceOver says. |

### A place

For a card whose question is a place's picture (a map, an outline): the app draws the place on a live map.

| Key | Type | Required | Rule |
|---|---|---|---|
| `code` | text | yes | The place's stable code: ISO 3166-1 alpha-3 where there is one (`"CHE"`), the deck's own otherwise. |
| `region` | object | yes | The region's name by language (`{"en": "Western Europe", "fr": "Europe de l’Ouest"}`), which VoiceOver reads. Never the place's own name: that is the answer. |
| `polygons` | list | yes | The outline: polygons, each a list of rings (the first the outer one), each ring a list of `{"longitude": …, "latitude": …}` in degrees. |
| `marks` | list | no | Up to 16 points in the same form, drawn as unlabeled dots (a capital). |

## The other fields

### RectoVerso search

Extra words a card can be found by, in a field named `RectoVerso search`, named in no template. It adds nothing to the review.

```json
{"v": 1, "fields": [{"name": "Continent", "values": ["Europe", "Asia"], "aliases": ["Eurasia"]}]}
```

Up to 32 fields with different names (up to 80 characters); each has 1 to 32 `values` and optionally up to 32 `aliases`, up to 256 characters each; plain text, no markup. The names and values are in the package's language. A record that breaks a rule is ignored, and the card is unaffected.

### RectoVerso place

For a note without a payload, the same place in a field named `RectoVerso place`, as GeoJSON:

```json
{"code": "CHE", "region": {"en": "Western Europe", "fr": "Europe de l’Ouest"},
 "outline": {"type": "Polygon", "coordinates": [[[5.96, 45.82], [10.49, 45.82], [10.49, 47.81], [5.96, 47.81], [5.96, 45.82]]]},
 "marks": {"type": "MultiPoint", "coordinates": [[7.45, 46.95]]}}
```

`outline` is a Polygon or a MultiPolygon, `[longitude, latitude]` in degrees, each ring closed; `marks` is optional, a MultiPoint or a Point, up to 16. The field holds up to 5 MiB, 1,024 polygons, 2,048 rings and 200,000 points. A note with a payload uses the payload's `place` instead: the field is not read.

### RectoVerso Occlusion

For a note without a payload, a [prepared figure](#a-prepared-figure) in a field named `RectoVerso Occlusion`: the text `RV-OCCLUSION-1:` followed by the preparation's JSON in Base64 (up to 256 KiB of JSON).
