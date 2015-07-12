#!/usr/bin/env python

import random
import sys

from drinks import recipe


# MUST MAP TO ORDER OF PHYSICAL VALVES
INGREDIENTS_ORDERED = (
    "bourbon",
    "bourbon_backup", #backup bottle
    "tequila",
    "tequila_backup", #backup bottle
    "galliano",
    "chocolate bitters", #small bottle location
    "scotch",
    "rye",
    "rum",
    "vodka",
    "triple sec",
    "frangelico",
    "angostura bitters", #small bottle location
    "sweet vermouth",
    "kahlua",
    "gin",
    "campari",
    "dry vermouth",
    "peychauds bitters", #small bottle location
    "agave",
    "pimms",
    "grenadine",
    "simple",
    "lemon",
    "lime",
    "orange bitters", #small bottle location
    "orange",
    "tonic",
    "cola",
    "water",
    "soda",
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
      ingredient = ingredient + "_backup"
  valve = ingredient_list.index(ingredient)
  return valve


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

