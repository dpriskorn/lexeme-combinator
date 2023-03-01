# Lexeme combinator
Simple CLI-tool to combine lexemes easily on Wikidata
![image](https://user-images.githubusercontent.com/68460690/220359748-8a8bbf67-6516-4adc-9414-7957e05b7ac7.png)

# Installation
Clone the git repo:

`$ git clone https://github.com/dpriskorn/lexeme-combinator.git`
`$ cd lexeme-combinator`

## Setup
We use pip and poetry to set everything up.

`$ pip install poetry && poetry install`

[Generate a botpassword](https://wikicitations.wiki.opencura.com/w/index.php?title=Special:UserLogin&returnto=Special%3ABotPasswords&returntoquery=&force=BotPasswords)

## Configuration
Copy config.py.sample -> config.py 
`$ cp config.py.sample config.py`
and 
enter your botpassword credentials. E.g. user: "test" and password: "q62noap7251t8o3nwgqov0c0h8gvqt20"
`$ nano config.py`

# Use
Run:

`poetry run python main.py`

This will promp you for each lexeme where 2 parts was successfully found.

# Thanks
Big thanks to Nikki and Mahir for helping 
with the SPARQL query that makes this possible.

# License
GPLv3+
