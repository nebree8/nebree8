#!/usr/bin/env python

import random
import sys

import logging

from drinks import recipe

BACKUP = '_backup'

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
    "tequila",
    "scotch",
    "mescal",
    "angostura bitters",  #small bottle location
    "simple syrup",
    "frangelico",
    "galliano",
    "triple sec",
    "kahlua",
    "peychauds bitters",
    "sweet vermouth",
    "grenadine",
    "lime juice",
    "agave syrup",
    "rum", #"bourbon_backup",
    "absinthe",
    "air",
    "tonic",
    "orange juice",
    "cola",
    "lemon juice",
    "soda",
)

OVERRIDES = {
    #"lime juice": "Lemon juice",
    #"rye" : "bourbon_backup",
    #"rum" : "bourbon",
    #"mescal" : "tequila",
}




def IngredientsOrdered():
  return INGREDIENTS_ORDERED


def IngredientNameToValvePosition(ingredient, drink_name):
  ingredient_list = IngredientsOrdered()
  ingredient = ingredient.lower()
  valve = ingredient_list.index(ingredient)
  return valve


def SubstituteIngredients(ingredients, drink_name):
  if drink_name in ("Prime", "Flush"):
    return
  for ingredient in ingredients:
    substitute = OVERRIDES.get(ingredient.name.lower(), None)
    if substitute:
      logging.info("Substituting %s => %s", ingredient.name, substitute)
      ingredient.name = substitute


def ReplaceWithBackups(ingredients, drink_name):
  """Random chance of replacing a ingredient with 'ingredient_backup'"""
  if drink_name in ("Prime", "Flush"):
    return
  for ingredient in ingredients:
    ingredient.name = ingredient.name.lower()
    if ingredient.name + BACKUP in INGREDIENTS_ORDERED:
      suffix = random.choice(["", BACKUP])
      ingredient.name = ingredient.name + suffix


def Validate():
  for i, ingredient_name in enumerate(INGREDIENTS_ORDERED):
    if not ingredient_name:
      continue
    if ingredient_name.endswith(BACKUP):
      assert ingredient_name[:-len(BACKUP)] in INGREDIENTS_ORDERED, \
          "No primary for " + ingredient_name
      assert INGREDIENTS_ORDERED.index(ingredient_name) == i, \
          "Duplicate ingredient " + ingredient_name
      assert ingredient_name.islower()
  for original, substitution in OVERRIDES.iteritems():
    assert original.islower()
    assert substitution.lower() in INGREDIENTS_ORDERED, \
        "Substitution %s for %s not in ingredients" % (substitution, original)

Validate()
