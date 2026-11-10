# Working on a deck

For any agent (Claude Code, Codex or another) working in a deck's repository, or in this kit. This file says how the work is done and where each rule lives. It doesn't repeat the rules: read the page named before the work it covers. A deck's own AGENTS.md adds that deck's rules; where the two differ on the contract, this kit wins.

## Before anything

- **The owner decides.** Coverage, names, conventions, categories, the sample, the covers, the study options, licenses, and every headline and description are the deck owner's. Bring each choice with a recommendation; never settle it in the deck.
- **Start only on an explicit go** ("go", "start it", "yes"). An answer that sharpens the scope isn't one.
- **Each decision gets a dated entry** in the deck's `docs/decisions.md`: the date, what was decided, by whom, and why. Earlier entries are history: never edit them.
- **Evidence before the owner sees anything.** Run the checks, look at the result, and say plainly what you couldn't check, with what it would take to check it.
- **Nothing merged, tagged, released or published without the owner's go,** given for that one step: a go for a merge isn't a go for the tag, the release, or a gallery's pin moved to it. A green check publishes nothing.
- **A branch per change, a pull request to merge.** Commit only your own files, by name. Never rewrite pushed history.
- **Packages, rendered pictures, caches and build output stay out of Git.** A tool takes its output path as an argument.

## 1. Deck authoring: the content

| Before you… | Read |
|---|---|
| Start a deck, or change its layout | [docs/getting-started.md](docs/getting-started.md) |
| Add, change or retire a card | [docs/versioning.md](docs/versioning.md#what-never-changes): content changes freely, identities never. |
| Make cards build on each other | [docs/prerequisites.md](docs/prerequisites.md) |
| Write a word a learner reads, in any language | [docs/languages.md](docs/languages.md) |
| Add a source, a picture or a sound | [docs/contract.md](docs/contract.md#credits-and-licenses): every source has its name, version, address and license, every picture its credit, and nothing is non-commercial or no-derivatives. |

- **Never invent a fact.** Every fact (a name, a date, a value, a border) is checked against an independent, citable source, recorded with the content. When sources disagree or a fact can't be verified, say so and bring it to the owner.
- **Every language a deck ships is complete,** and has as many cards as the others.
- **New-card stages are an introduction order,** never a scheduler or an entitlement: where a deck sorts its new cards into stages, they say only which cards come first.
- **A retired question keeps its note,** so its history stays; how it leaves the reviews is the owner's call.
- **A private deck stays private:** its cards, pictures, sounds, packages, samples and screenshots never go into a public repository, an issue, a pull request, a chat or a test fixture. A public trace says counts and ids, nothing a learner would pay for.

## 2. Contract honoring: what the app reads

| Before you… | Read |
|---|---|
| Touch `rectoverso.json` | [docs/contract.md](docs/contract.md) |
| Touch a note's `RectoVerso` field, or the other fields the app reads | [docs/card-payload.md](docs/card-payload.md) |
| Touch `scripts/source_data.py` | [docs/getting-started.md](docs/getting-started.md#4-write-scriptssource_datapy) |
| Prepare a version or a release | [docs/versioning.md](docs/versioning.md) |

- **Run `python3 kit/check.py` after every change,** and read [docs/check.md](docs/check.md) for a refusal. A deck isn't done until it passes.
- **Never use a field, a value or a form the kit doesn't describe.** What only a deck knows, the app can't read. A new one is a change to the contract, made in this kit first ([CONTRIBUTING.md](CONTRIBUTING.md)).
- **The kit is pinned.** Moving it is a pull request of its own ([docs/versioning.md](docs/versioning.md#moving-to-a-new-version)). Never edit files under `kit/` from a deck.

## 3. Cover making: a gallery's pictures

Read [docs/covers.md](docs/covers.md). The check holds the names and the lists; the picture itself (its size, its safe area, how it reads small, in light and in dark) is checked by eye, and the choice of covers is the owner's.

## Before the owner sees a candidate

1. The deck's own checks (its AGENTS.md names them).
2. `python3 kit/check.py`.
3. Anki: each package opens with its cards and media, and an update over the previous version keeps every review, with no duplicates.
4. RectoVerso: the deck in the app, its sample, its cards in light and dark, in every language. Say what couldn't be checked.

## Working on the kit itself

Read [CONTRIBUTING.md](CONTRIBUTING.md). Run `python3 -m unittest discover -s tests` before every pull request; the tests hold the docs, the schemas and the check together.
