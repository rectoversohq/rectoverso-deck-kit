# Prerequisites: cards that build on each other

In a course, some cards only make sense after others. A word in Morse code is noise until you have met its letters; a kana's listening question is a guess until you have seen the kana. A deck says so card by card, and the app's **Lesson mode** then holds a card back until what it builds on has been taught.

## Two lists

A card's [payload](card-payload.md) may carry two optional lists of tokens:

- `introduces`: what the card teaches.
- `requires`: what the card builds on.

```json
{"v": 1, "book": "…", "card": "…", "kind": "basic", "introduces": ["e"]}
{"v": 1, "book": "…", "card": "…", "kind": "basic", "requires": ["a", "e", "t"]}
```

A token is the deck's own word for one thing taught: lowercase words and digits, with hyphens between them (`e`, `hira-3042`, `rule-dakuten`). The app never reads a meaning into it, and a token of one deck means nothing to another. Each language's package is a deck of its own: what is taught in the English edition teaches nothing in the French.

## Writing them

- **Only a card that teaches introduces.** A card introduces a thing when answering it shows the learner that thing whole: a letter's own card, a kana's reading card, a rule's first example. A card that merely uses a thing doesn't introduce it.
- **A card requires everything it shows or asks that another card teaches.** The word TEA requires t, e and a. A figure that shows other items beside the one it asks requires those too: a table of five kana with one covered still shows the other four.
- **Leave the lists out** on a card that builds on nothing and teaches nothing others need. A deck with no lists at all studies as any deck.
- **Write the deck in an order that teaches before it asks.** The order of the notes is the deck's own order, the one a learner follows with new cards in the deck's order. Every card comes after the cards that introduce what it requires.

## What the check holds

For each language's package, the check reads every note's payload as the app does and refuses:

| Refusal | What is wrong |
|---|---|
| A list that isn't one of tokens | `requires` or `introduces` isn't a list, holds something that isn't a token, or names one twice. |
| A token no card introduces | A card requires something that no card of the same package introduces: it could never come. Often a typo, or a token introduced only in another language's source. |
| Cards waiting for each other | A card requires what it introduces itself, or two cards each wait for the other. Neither could ever come. |
| An order that asks before it teaches | Every card's turn can come, but not in the order written: a card stands before the card that introduces what it requires. Move it after. |

[The check](check.md#prerequisites) has the exact messages.

## What the app does

With **Lesson mode** on (a switch in a deck's **Deck options**, shown only on a deck that declares prerequisites, and on by default):

- **Taught means shown, not mastered.** A token is taught once a card that introduces it has been answered, right or wrong: every answer shows the whole answer. A first failed recall holds nothing back.
- **A card that waits isn't due.** New or already studied, it stays out of the day's cards, and takes none of the day's new cards: the next card whose turn can come does. Nothing is ever added to a day.
- **Any order is put right.** With new cards at random, a card is taken only once the cards before it teach what it requires. So a deck opened as a plain file, without a gallery's study options, still never asks before it teaches.
- **A teaching card that is suspended or removed** before it was answered teaches nothing: what builds on it waits until it is back.
- **Practice** follows the same rule for a practice of the whole deck. A practice of a search or a filter asks exactly the cards the learner chose.
- **The learner can turn it off,** and the deck then studies as any deck.

So prerequisites are a promise the author makes once, in the package, and the app keeps whatever the learner's options are. They are not a lock on mastery: nothing waits for a card to be known well.

## An example

The [example deck](../examples/morse-starter) teaches four letters and three words. In English:

| Card | Introduces | Requires |
|---|---|---|
| E | `e` | |
| T | `t` | |
| A | `a` | |
| TEA | | `a`, `e`, `t` |
| N | `n` | |
| NET | | `e`, `n`, `t` |
| ANT | | `a`, `n`, `t` |

With four new cards a day in the deck's order, the first day is E, T, A, TEA. Suspend A before answering it, and TEA and ANT wait; NET still comes.
