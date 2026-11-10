# Languages

One deck, several languages. This page says how a deck holds them, and the rules for the words a learner reads in English and in French, the two languages RectoVerso itself speaks.

## One repository, one package a language

- **One repository holds every language.** What the languages share (the facts, the pictures, the sounds, the builders) is kept once; each language's words live beside it.
- **Each language is a package of its own:** its own `.apkg`, its own package id, its own note GUIDs (`<guidPrefix>-<language>-…`), its own Anki note type and deck ids. A learner picks a language before adding the deck. Two languages installed together never collide, and adding or changing one never touches another's progress.
- **Every language a deck ships is complete:** its title, subject, headline and description, its notes for this edition, and every card. A language half done isn't shipped.
- **Every language has the same number of cards** (`cards`). A card that only makes sense in one language has its counterpart in the others (the example deck's English word TEA is the French edition's TATA).
- **A card's content is the author's.** The rules below are for the words around the cards (titles, descriptions, instructions, notes), and for cards the deck writes itself. Quoted material stays as its source has it.

A language's code is two lowercase letters, with optional parts after a hyphen: `en`, `fr`, `pt-BR`.

## English

- **American English:** math, color, gray, center, license, canceled, memorize.
- **Short, plain sentences,** one idea each. Calm: no exclamation marks, no cheerleading.
- **"You" for the learner.** Say the concrete thing: "Read this word." rather than "Test your reading skills!".
- **An instruction says what to do with this card,** in a few words, the same words on every card of its kind: "Read this letter.", "Which hiragana?".
- **Typography:** the ellipsis as one character (…); "·" as a separator; a percentage without a space ("40%").

## French

France's French, for every French-speaking learner.

- **Vous, always.** Never *tu*, and never the bare infinitive for an instruction: « Lisez ce mot. », not « Lire ce mot ».
- **Short, plain sentences, like the English.** French runs 15 to 30% longer: cut words, never meaning.
- **Sentence case** for titles: « Tableau périodique », never « Tableau Périodique ». Capitals keep their accents: « État », « À réviser ».
- **Loanwords** as French learners keep them: *un deck*, *des decks*.

Typography, which the eye catches at once:

| Rule | Right | Wrong |
|---|---|---|
| Guillemets, with a narrow no-break space (U+202F) inside | « Tardigrade » | "Tardigrade" |
| A narrow no-break space (U+202F) before ; : ! ? and % | Désactivé : rien · 40 % | Désactivé: rien · 40% |
| The typographic apostrophe | l’eau | l'eau |
| The ellipsis as one character, no space before it | Importer… | Importer ... |
| Ordinals | 1er, 1re, 2e, XIXe siècle | 2ème, 2nd |
| An en dash, spaced, for a parenthesis | le thé – ou le café | le thé - ou le café |

Numbers: a thousand is « 1 234 » and a decimal « 0,5 ». Zero is singular: « 0 carte ».

Genders the words around a deck need: *une carte*, *un deck*, *une révision*, *une étiquette*. Participles and adjectives agree: « 2 cartes ajoutées », « 2 decks ajoutés ».

## Names never translated

RectoVerso, Anki, and the names of people, works and software.

## What the check holds

The check holds that every text is there in every language. It doesn't read the words: the typography and the voice are yours to check, line by line, before a release.
