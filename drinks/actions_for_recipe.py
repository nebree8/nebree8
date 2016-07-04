import logging

from actions.compressor import CompressorToggle
from actions.compressor import State
from actions.home import Home
#from actions.meter import Meter
#from actions.meter_dead_reckoned import MeterDeadReckoned as Meter
from actions.led import SetLedForValve
from actions.meter_simple import MeterSimple as Meter
from actions.meter_bitters import MeterBitters
from actions.move import Move
from actions.wait_for_glass_removal import WaitForGlassRemoval
from actions.wait_for_glass_placed import WaitForGlassPlaced
from actions.dispense_cup import DispenseCup, ReleaseCup
from actions.ice import DispenseIce
from actions.pressurize import HoldPressure, ReleasePressure
from config import valve_position, ingredients

def actions_for_recipe(recipe):
  """Returns the actions necessary to make the given recipe.

    recipe: manual_db.Recipe
    """
  logging.info("Enqueuing actions for recipe %s", recipe)
  actions = []
  sorted_ingredients = sorted(
      recipe.ingredients,
      key=lambda i: -ingredients.IngredientNameToValvePosition(i.name, recipe.name))
  for ingredient in sorted_ingredients:
    valve = ingredients.IngredientNameToValvePosition(ingredient.name,
                                                      recipe.name)
    actions.append(SetLedForValve(valve, 255, 0, 0))
  #actions.append(Move(-57.875))
  #actions.append(DispenseIce())
  for ingredient in sorted_ingredients:
    valve = ingredients.IngredientNameToValvePosition(ingredient.name,
                                                      recipe.name)
    actions.append(Move(valve_position(valve)))
    actions.append(SetLedForValve(valve, 0, 255, 0))
    if hasattr(ingredient.qty, 'drops'):
      actions.append(MeterBitters(valve_to_actuate=valve,
                                  drops_to_meter=ingredient.qty.drops))
    elif hasattr(ingredient.qty, 'oz'):
      actions.append(Meter(valve_to_actuate=valve,
                           oz_to_meter=ingredient.qty.oz))
    else:
      raise Exception("Ingredient %s has no quantity for recipe %s:\n%s",
                      ingredient.name, recipe.name, recipe)
    actions.append(SetLedForValve(valve, 0, 128, 255))
  actions.append(Move(0.0))
  #actions.append(Move(0.0))
  actions.append(Home(carefully=False))
  actions.append(WaitForGlassRemoval(recipe.user_name, recipe))
  for ingredient in sorted_ingredients:
    valve = ingredients.IngredientNameToValvePosition(ingredient.name,
                                                      recipe.name)
    actions.append(SetLedForValve(valve, 0, 0, 0))
  #actions.append(WaitForGlassPlaced())
  return actions
