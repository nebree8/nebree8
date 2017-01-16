#!/usr/bin/python
"""Generate and run a recipe to prime bitters."""

from sys import argv

import common
import gflags

from config.ingredients import INGREDIENTS_ORDERED
from drinks.recipe import Recipe, Ingredient, Drops, Oz
from drinks.actions_for_recipe import actions_for_recipe

"""
BITTERS = set([
    'angostura bitters',
    'peychauds bitters',
    'rose',
])
"""

BITTERS = set([
    'agave syrup',
])


def main(robot):
  ingredients = []
  for name in INGREDIENTS_ORDERED:
    if name in BITTERS:
      ingredients.append(Ingredient(Oz(1), name))

  recipe = Recipe('prime-bitters', ingredients)
  print recipe

  for action in actions_for_recipe(recipe):
    print action
    action(robot)


if __name__ == "__main__":
  main(common.make_robot())
