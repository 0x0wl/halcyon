# halcyon
another IRC bot

Halcyon is an IRC bot originally designed to operate on Purdue's Dtella network. It constructs word ladders between english words.

| command         | description                                                                                          |
| --------------- | ---------------------------------------------------------------------------------------------------- |
| x/word          | replaces 'word' with another english word that differs by one letter.                                |
| y/word          | fetches the last message sent in IRC containing 'word' (currently logs up to 100 messages at a time) |
| !wl word1 word2 | returns a word ladder from word1 to word2.                                                           |
