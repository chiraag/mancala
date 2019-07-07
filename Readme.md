# Mancala

A simple implementation of the [Mancala](https://en.wikipedia.org/wiki/Mancala) game. The rule variant implemented here is:
- Board Size: $2 \times 6$
- Seeds per hole: $4$
- Move ending on player's home results in free turn
- Move ending on an empty hole "captures" all seeds from the opposite hole
- Player never seeds opponent's home
- Player may optionally skip seeding own home

## Usage

The barebones 2-player game is implemented in the `rules.py` file and may be invoked as `python rules.py`. Both players take turns typing their moves. Valid moves conform to the regular expression `\d+[s]?` where `\d+` indicates the chosen hole to start seeding and the final `[s]?` indicates the optional skipping of the player's home.