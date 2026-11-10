# Covers

A cover is a picture a gallery shows of a deck: in its list, on the deck's page, in a pile the learner can leaf through. Covers are optional. A deck that has them has both kinds, light and dark, in every language it ships.

## The picture

| Rule | Why |
|---|---|
| **3:2**, at least 2,010 pixels wide (so 2,010 × 1,340 or larger). | The widest place a cover is shown is 669 points across at three pixels a point. |
| **The subject sits in the middle:** inside the middle 78% of the width and 66% of the height. | A cover is cropped around its middle wherever it is shown: a wide box, a small thumbnail, a square tile. Only that middle area shows in every crop. |
| **Nothing that matters in the top trailing corner** (top right in English and French), 20% of the width by 25% of the height. | The gallery puts the language's pill there. |
| **No title in the picture.** | The gallery sets the deck's title beside the cover. Other words are fine, in the language the cover is listed for. |
| **PNG,** or JPEG for a photograph. | |

One picture may serve both light and dark mode, and one picture without words may serve every language.

## The name

```
<guidPrefix>[-<language>]-cover[-<light|dark>]-<n>.png      (.jpg for a photograph)
```

- **The deck's GUID prefix first,** so two decks' covers never share a name.
- **A language** only on a cover with words, its language's alone: `rv-capitals-fr-cover-2.png`. A cover without words has none, and every language may list it: `rv-capitals-cover-1.png`.
- **An appearance** only on a cover made for light or for dark mode: `ex-morse-cover-dark-1.png`. A cover without one may be listed for both.
- **A number,** from 1, in the order shown.

## In rectoverso.json

```json
"covers": {
  "en": {"light": ["rv-capitals-cover-1.png", "rv-capitals-en-cover-2.png"],
         "dark":  ["rv-capitals-cover-1.png", "rv-capitals-en-cover-dark-2.png"]},
  "fr": {"light": ["rv-capitals-cover-1.png", "rv-capitals-fr-cover-2.png"],
         "dark":  ["rv-capitals-cover-1.png", "rv-capitals-fr-cover-dark-2.png"]}
}
```

- Every language in `languages` has an entry, with exactly `light` and `dark`.
- Each list has one cover or more, in the order the gallery shows them, each once.
- A cover named for one appearance is only in that appearance's list. A cover named for a language is only in that language's lists.

## Making and shipping them

Keep each cover's master (a vector file, a layered picture) in the repository, for instance under `artwork/covers/`, and have the deck's build render the PNGs into its output beside the packages. The rendered files stay out of Git. They are attached to the deck's release with the packages, and listed in the release's `SHA256SUMS` ([Versioning](versioning.md#a-release)).

The check holds the names and the lists. It doesn't open a picture: its size, its safe area and how it reads at thumbnail size are yours to check, in light and in dark.
