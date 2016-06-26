#!/usr/bin/env python

import random
import sys

from drinks import recipe


# MUST MAP TO ORDER OF PHYSICAL VALVES
INGREDIENTS_ORDERED = (
   "vodka",
   "gin",
   "bourbon", # "bourbon",
   "tequila",
   "rum",
   "dry vermouth",
   "chocolate bitters", #small bottle location # WILL
   "rye",
   "pimms",  # WILL
   "campari",
   "scotch", # no ice
   "amaretto",
   "angostura bitters", #small bottle location
   "simple",
   "frangelico",
   "peppermint schnapps", # peppermint schnapps
   "triple sec", # MISSING
   "kahlua",
   "peychauds bitters", #small bottle location # WILL
   "sweet vermouth", # MISSING
   "grenadine",
   "lime",
   "agave",  # NOT LINED UP
   "peach schnapps",  # HALLOWEEN: OUT OF GALLIANO
   "triple sec_backup", # MISSING
   "soda",
   "orange",
   "air",
   "tonic",
   "lemon",
   "maple syrup",

   #"honey", #backup bottle
   #"maple", #backup bottle
   #"orange bitters", #small bottle location
   #"water",
)

OVERRIDES = {
#    tuple(range(0, 11)) : "air",
}

def IngredientsOrdered():
  ingredient_list = list(INGREDIENTS_ORDERED)
  for indices, value in OVERRIDES.iteritems():
    for index in indices:
      ingredient_list[index] = value
  return ingredient_list


def IngredientNameToValvePosition(ingredient, drink_name):
  ingredient_list = IngredientsOrdered()
  ingredient = ingredient.lower()
  ingredient = ingredient.replace(" juice", "")
  ingredient = ingredient.replace(" syrup", "")
  if drink_name != "Prime":
    if ingredient + "_backup" in ingredient_list:
      suffix = random.choice(["", "_backup"])
      ingredient = ingredient + suffix
  valve = ingredient_list.index(ingredient)
  return valve


SCALE = 0.9


def ScaleDrinkSize(ingredient_list):
  pass
  # total_desired_oz = 4
  # total_oz = 0
  # for ingredient in ingredient_list:
  #   if type(ingredient.qty) == recipe.Oz:
  #     total_oz += ingredient.qty.oz
  # adjustment = total_desired_oz * 1.0 / total_oz
  # for ingredient in ingredient_list:
  #   if type(ingredient.qty) == recipe.Oz:
  #     ingredient.qty.oz *= adjustment

