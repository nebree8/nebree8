from drinks.random_drinks import INGREDIENTS


def water_down_recipe(recipe, alcohol_ratio=.9):
  """Take a recipe and water down the alcohol by the given ratio."""
  for ingredient in recipe.ingredients:
    ratios = INGREDIENTS.get(ingredient.name.lower(), [0] * 5)
    if ratios[0] > 0 and ingredient.qty.parts:
      ingredient.qty.parts *= alcohol_ratio
  return recipe
