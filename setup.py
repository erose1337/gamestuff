from setuptools import setup

#with open(".\\pride\\readme.md", 'r') as _file:
#    long_description = _file.read()
    
options = {"name" : "game",
           "version" : "0.0.1a",
           
           "author" : "Ella Rose",
           "author_email" : "python_pride@protonmail.com",
           "packages" : ["game", "game.items", "game.items.magic", "game.items.melee", "game.items.range",
                         "game.skills"]}
setup(**options)
