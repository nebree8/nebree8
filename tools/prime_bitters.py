#!/usr/bin/python
"""Generate and run a recipe to prime bitters."""

from sys import argv

import gflags

# Hack import path to include parent directory.
from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

from physical_robot import PhysicalRobot as Robot
#from fake_robot import FakeRobot as Robot
from config.ingredients import INGREDIENTS_ORDERED
from drinks.recipe import Recipe, Ingredient, Oz
from drinks.actions_for_recipe import actions_for_recipe

BITTERS = set([
    'angostura bitters',
    'peychauds bitters',
    'rose',
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
  gflags.FLAGS(argv)
  main(Robot())
