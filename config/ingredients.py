#!/usr/bin/env python

import random
import sys

from drinks import recipe


# MUST MAP TO ORDER OF PHYSICAL VALVES
INGREDIENTS_ORDERED = (
    "air",
    "air",
    "air",
    "air",
    "air",
    "air",
    "air",
    "air",
    "air",
    "air",
    "air",
    "air",
    "air",
#   "bourbon",
#   "bourbon", #backup bottle
#   "tequila",
#   "tequila", #backup bottle
#   "galliano",
#   "chocolate bitters", #small bottle location
#   "scotch",
#   "rye",
#   "rum",
#   "vodka",
#   "triple sec",
#   "frangelico",
#   "angostura bitters", #small bottle location
#   "sweet vermouth",
#   "kahlua",
#   "gin",
#   "campari",
#   "dry vermouth",
#   "peychauds bitters", #small bottle location
#   "agave",
#   "pimms",
#   "grenadine",
#   "simple",
#   "lemon",
#   "lime",
#   "orange bitters", #small bottle location
#   "orange",
#   "tonic",
#   "cola",
#   "water",
#   "soda",
)

def ScaleDrinkSize(ingredient_list):
  total_desired_oz = 4
  total_oz = 0
  for ingredient in ingredient_list:
    if type(ingredient.qty) == recipe.Oz:
      total_oz += ingredient.qty.oz
  adjustment = total_desired_oz * 1.0 / total_oz
  for ingredient in ingredient_list:
    if type(ingredient.qty) == recipe.Oz:
      ingredient.qty.oz *= adjustment

