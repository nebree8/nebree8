#!/usr/bin/env python
import copy

from recipe import Recipe, Ingredient, Oz, Parts, Drops
from config import ingredients

db = [
    Recipe(
        name = 'Margarita',
        total_oz = 2.75,
        ingredients = [
            Ingredient(Parts(2), 'Tequila'),
            Ingredient(Parts(1), 'Lime Juice'),
            Ingredient(Parts(1), 'Agave Syrup')]),
    Recipe(
        name = 'Old Fashioned',
        total_oz = 3,
        ingredients = [
            Ingredient(Parts(4), 'Bourbon'),
            Ingredient(Parts(1), 'Simple Syrup'),
            Ingredient(Drops(2), 'Angostura Bitters')]),
    Recipe(
        name = 'Daquiri',
        total_oz = 2.75, #topped off with soda
        ingredients = [
            Ingredient(Parts(2), 'Rum'),
            Ingredient(Parts(1), 'Lime Juice'),
            Ingredient(Parts(1), 'Simple Syrup')]),
    Recipe(
        name = 'Gin Gimlet', #top with tonic to be a G&T
        total_oz = 2.75,
        ingredients = [
            Ingredient(Parts(6), 'Gin'),
            Ingredient(Parts(1), 'Lime Juice'),]),
    Recipe(
        name = 'Whiskey Sour',
        total_oz = 2.75,
        ingredients = [
            Ingredient(Parts(2), 'Rye'),
            Ingredient(Parts(1), 'Lemon Juice'),
            Ingredient(Parts(1), 'Simple Syrup')]),
    Recipe(
        name = 'Pimms Cup',
        total_oz = 4,
        ingredients = [
            Ingredient(Parts(6), 'Gin'),
            Ingredient(Parts(3), 'Pimms'),
            Ingredient(Parts(1), 'Lemon Juice'),
            Ingredient(Parts(1), 'Simple Syrup')]),
    Recipe(
        name = 'Negroni',
        total_oz = 2.75,
        ingredients =[
            Ingredient(Parts(1), 'Gin'),
            Ingredient(Parts(1), 'Sweet Vermouth'),
            Ingredient(Parts(1), 'Campari')]),
    Recipe(
        name = 'Boulevardier',
        total_oz = 2.75,
        ingredients = [
            Ingredient(Parts(1.5), 'Rye'),
            Ingredient(Parts(1), 'Campari'),
            Ingredient(Parts(1), 'Sweet Vermouth')]),
    Recipe(
        name = 'Americano',
        total_oz = 5,
        ingredients = [
            Ingredient(Parts(1), 'Campari'),
            Ingredient(Parts(1), 'Sweet Vermouth'),
            Ingredient(Parts(3), 'Soda')]),
    Recipe(
        name = 'Manhattan',
        total_oz = 4,
        ingredients = [
            Ingredient(Parts(5), 'Rye'),
            Ingredient(Parts(2), 'Sweet Vermouth'),
            Ingredient(Drops(2), 'Angostura Bitters')]),
    Recipe(
        name = 'Gin & Tonic',
        total_oz = 5,
        ingredients = [
            Ingredient(Parts(3), 'Gin'),
            Ingredient(Parts(1), 'Tonic')]),
    Recipe(
        name = 'Scotch (neat)',
        total_oz = 2,
        ingredients = [
            Ingredient(Parts(1), 'Scotch')]),
    Recipe(
        name = 'Scotch & Water',
        total_oz = 3,
        ingredients = [
            Ingredient(Parts(3), 'Scotch'),
            Ingredient(Parts(1), 'Water')]),
    Recipe(
        name = 'Screwdriver',
        total_oz = 5,
        ingredients = [
            Ingredient(Parts(2), 'Vodka'),
            Ingredient(Parts(3), 'Orange')]),
    Recipe(
        name = 'Hairy Navel',
        total_oz = 5,
        ingredients = [
            Ingredient(Parts(1), 'Vodka'),
            Ingredient(Parts(1), 'Triple Sec'),
            Ingredient(Parts(2), 'Orange')]),
    Recipe(
        name = 'Tequila Sunrise',
        total_oz = 5,
        ingredients = [
            Ingredient(Parts(3), 'Tequila'),
            Ingredient(Parts(6), 'Orange'),
            Ingredient(Parts(1), 'Grenadine')]),
    Recipe(
        name = 'Cuba Libre',
        total_oz = 4,
        ingredients = [
            Ingredient(Parts(5), 'Rum'),
            Ingredient(Parts(1), 'Lime'),
            Ingredient(Parts(12), 'Cola')]),
    Recipe(
        name = 'Rum & Coke',
        total_oz = 5,
        ingredients = [
            Ingredient(Parts(2), 'Rum'),
            Ingredient(Parts(3), 'Cola')]),
    Recipe(
        name = 'Godfather',
        total_oz = 2.75,
        ingredients = [
            Ingredient(Parts(1), 'Scotch'),
            Ingredient(Parts(1), 'Frangelico')]),
    Recipe(
        name = 'Harvey Wallbanger',
        total_oz = 5,
        ingredients = [
            Ingredient(Parts(3), 'Vodka'),
            Ingredient(Parts(1), 'Galliano'),
            Ingredient(Parts(6), 'Orange')]),
    Recipe(
        name = 'Dry Martini',
        total_oz = 2.75,
        ingredients = [
            Ingredient(Parts(6), 'Gin'),
            Ingredient(Parts(1), 'Dry Vermouth')]),
    Recipe(
        name = 'Original Martini',
        total_oz = 2.75,
        ingredients = [
            Ingredient(Parts(2), 'Gin'),
            Ingredient(Parts(1), 'Dry Vermouth')]),
    Recipe(
        name = 'Perfect Martini',
        total_oz = 2.75,
        ingredients = [
            Ingredient(Parts(1), 'Gin'),
            Ingredient(Parts(1), 'Dry Vermouth')]),
    Recipe(
        name = 'Vodka Martini',
        total_oz = 2.75,
        ingredients = [
            Ingredient(Parts(6), 'Vodka'),
            Ingredient(Parts(1), 'Dry Vermouth')]),
    Recipe(
        name = 'Bronx',
        total_oz = 2.75,
        ingredients = [
            Ingredient(Parts(6), 'Gin'),
            Ingredient(Parts(2), 'Dry Vermouth'),
            Ingredient(Parts(3), 'Sweet Vermouth'),
            Ingredient(Parts(3), 'Orange')]),
    Recipe(
        name = 'Gin Fizz',
        total_oz = 5,
        ingredients = [
            Ingredient(Parts(4.5), 'Gin'),
            Ingredient(Parts(3), 'Lemon Juice'),
            Ingredient(Parts(1), 'Simple Syrup'),
            Ingredient(Parts(8), 'Soda')]),
    Recipe(
        name = 'Yellow Bird',
        total_oz = 5,
        ingredients = [
            Ingredient(Parts(2), 'Rum'),
            Ingredient(Parts(1), 'Lime Juice'),
            Ingredient(Parts(1), 'Triple Sec'),
            Ingredient(Parts(1), 'Galliano')]),
    Recipe(
        name = 'Kamikaze',
        total_oz = 2.75,
        ingredients = [
            Ingredient(Parts(1), 'Vodka'),
            Ingredient(Parts(1), 'Lime Juice'),
            Ingredient(Parts(1), 'Triple Sec')]),
    Recipe(
        name = 'Lemon Drop',
        total_oz = 2.75,
        ingredients = [
            Ingredient(Parts(2), 'Vodka'),
            Ingredient(Parts(1), 'Lemon Juice'),
            Ingredient(Parts(1), 'Simple Syrup')]),
    Recipe(
        name = 'Long Island Ice Tea',
        total_oz = 5,
        ingredients = [
            Ingredient(Parts(1), 'Vodka'),
            Ingredient(Parts(1), 'Gin'),
            Ingredient(Parts(1), 'Tequila'),
            Ingredient(Parts(1), 'Rum'),
            Ingredient(Parts(1), 'Lemon Juice'),
            Ingredient(Parts(1), 'Lime Juice'),
            Ingredient(Parts(1), 'Simple Syrup'),
            Ingredient(Parts(1), 'Triple Sec'),
            Ingredient(Parts(0.5), 'Cola')]),
    Recipe(
        name = 'Tom Collins',
        total_oz = 2.75,
        ingredients = [
            Ingredient(Parts(2), 'Gin'),
            Ingredient(Parts(1), 'Lemon Juice'),
            Ingredient(Parts(1), 'Simple Syrup')]),
    Recipe(
        name = 'Virgin Lemonade',
        total_oz = 2.75,
        ingredients = [
            Ingredient(Parts(1), 'Lemon Juice'),
            Ingredient(Parts(1), 'Simple Syrup')]),
    Recipe(
        name = 'Grenadine Punch',
        total_oz = 2.75,
        ingredients = [
            Ingredient(Parts(2), 'Grenadine'),
            Ingredient(Parts(1), 'Lemon Juice'),
            Ingredient(Parts(1), 'Lime Juice')]),
    Recipe(
        name = 'Random Sour',
        total_oz = 4.0,
        ingredients = [
            Ingredient(Parts(2), 'Alcohol'),
            Ingredient(Parts(1), 'Sweet'),
            Ingredient(Parts(1), 'Sour')]),
    Recipe(
        name = 'Random Boozy',
        total_oz = 3,
        ingredients = [
            Ingredient(Parts(4), 'Alcohol'),
            Ingredient(Parts(1), 'Sweet'),
            Ingredient(Drops(1), 'Bitters')]),
    Recipe(
        name = 'Random Bubbly Boozy',
        total_oz = 3,
        ingredients = [
            Ingredient(Parts(4), 'Alcohol'),
            Ingredient(Parts(1), 'Sweet'),
            Ingredient(Parts(1), 'Soda'),
            Ingredient(Drops(1), 'Bitters')]),
    Recipe(
        name = 'Random Bubbly Sour',
        total_oz = 3,
        ingredients = [
            Ingredient(Parts(2), 'Alcohol'),
            Ingredient(Parts(1), 'Sweet'),
            Ingredient(Parts(1), 'Sour'),
            Ingredient(Parts(1), 'Soda')]),
    Recipe(
        name = 'Custom Ice',
        total_oz = .1,
        ingredients = [
            Ingredient(Parts(0), 'Agave'),
            Ingredient(Parts(0), 'Grenadine'),
            Ingredient(Parts(1), 'Simple'),
            Ingredient(Parts(0), 'Lemon'),
            Ingredient(Parts(0), 'Lime'),
            Ingredient(Parts(0), 'Orange'),
            Ingredient(Parts(0), 'Tonic'),
            Ingredient(Parts(0), 'Cola'),
            Ingredient(Parts(0), 'Water'),
            Ingredient(Parts(0), 'Soda'),
            Ingredient(Drops(0), 'Chocolate Bitters'),
            Ingredient(Drops(0), 'Angostura Bitters'),
            Ingredient(Drops(0), 'Peychauds Bitters'),
            Ingredient(Drops(0), 'Orange Bitters')]),
]

TEST_DRINK = Recipe(
        name = 'Test drink',
        total_oz = 2.75,
        ingredients = [
            Ingredient(Parts(2), 'Vodka'),
            Ingredient(Parts(1), 'Bourbon'),
            Ingredient(Parts(1), 'Rye'),
            Ingredient(Parts(1), 'Rum')])

def LiveDB():
  live_ingredients = ingredients.IngredientsOrdered()
  live_db = []
  for drink in db:
    all_ingredients_live = True
    for ingredient in drink.ingredients:
      if ingredient.name.lower().replace(" juice", "").replace(" syrup", "") not in live_ingredients:
        print "dont have: %s" % ingredient.name
        all_ingredients_live = False
    if all_ingredients_live or "Random" in drink.name:
      print "adding: %s" % drink.name
      live_db.append(Recipe(name=drink.name, ingredients=drink.ingredients,
                            total_oz=drink.total_oz * ingredients.SCALE))
    else:
      print "skipping: %s" % drink.name
  return live_db



if __name__ == "__main__":
    for r in db:
        print r
