#!/usr/bin/env python

import random
import sys

from drinks import recipe


# MUST MAP TO ORDER OF PHYSICAL VALVES
INGREDIENTS_ORDERED = (
    "angostura bitters",
    "lime juice",
    "lemon juice",
    "grenadine", # brown bottle dark liquid
    "agave syrup", # clear bottle amber liquid
    "simple syrup",
    "kahlua",
    "pimms",
    "triple sec",
    "tequila",
    "gin",
    "rum",
    "rye",
    "bourbon",
    "vodka",
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

