#!/usr/bin/env python

import random
import sys

from drinks import recipe

# MUST MAP TO ORDER OF PHYSICAL VALVES
INGREDIENTS_ORDERED = (
    "vodka",
    "gin",
    "bourbon",
    "tequila",
    "rum",
    "dry vermouth",
    "rose",
    "rye",
    "campari",
    "rye_backup",
    "bourbon_backup",
    "gin_backup",
    "angostura bitters",  #small bottle location
    "simple syrup",
    "frangelico",
    "galliano",
    "triple sec",
    "kahlua",
    "cola",
    "sweet vermouth",
    "grenadine",
    "lime juice",
    "agave syrup",
    "tequila_backup",
    "mescal",
    "soda",
    "orange juice",
    "water",
    "tonic",
    "lemon juice",
    "rum_backup",
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
