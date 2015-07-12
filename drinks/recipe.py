
class Recipe(object):
    def __init__(self, name, ingredients, total_oz=None, user_name=None):
        self.name = name
        self.total_oz = total_oz
        self.ingredients = ingredients
        has_parts = any(isinstance(i.qty, Parts) for i in ingredients)
        if has_parts:
            if total_oz is None:
                raise Exception("Set total_oz for drink %s" % name)
            self.total_parts = sum(getattr(i.qty, 'parts', 0) for i in ingredients)
            for i in self.ingredients:
                i.qty.total_oz = total_oz
                i.qty.total_parts = self.total_parts
        if user_name:
          self.user_name = user_name

    def __str__(self):
        return "%s\n  %s\n\n" % (self.name, "\n  ".join(map(str, self.ingredients)))

    @property
    def json(self):
        return {
            'drink_name': self.name,
            'total_oz': self.total_oz,
            'ingredients': [i.json for i in self.ingredients],
        }

    @staticmethod
    def from_json(obj):
        return Recipe(name=obj['drink_name'], total_oz=obj['total_oz'],
                      ingredients=[Ingredient.from_json(i) for i in obj['ingredients']],
                      user_name=obj.get('user_name', None))


class Ingredient(object):
    def __init__(self, qty, name):
        assert issubclass(qty.__class__, Unit)
        self.qty = qty
        self.name = name
    def __str__(self):
        return "% 6s %s" % (self.qty, self.name.replace("_backup", ""))

    @staticmethod
    def from_json(obj):
        UNITS = {'oz': Oz, 'parts': Parts, 'drops': Drops}

        qty = None
        for k, v in obj.iteritems():
            if k in UNITS:
                qty = UNITS[k](v)
        if not qty:
            raise ValueError('Unsupported quantity for ingredient: %s', obj)
        return Ingredient(qty, obj['name'])

    @property
    def json(self):
        o = {'name': self.name}
        o.update(self.qty.json)
        return o

class Unit(object):
    def __str__(self):
        return "%.2f oz" % self.oz


class Oz(Unit):
    def __init__(self, oz):
        self.oz = oz
    @property
    def json(self):
        return {'oz': self.oz}


class Parts(Unit):
    def __init__(self, parts):
        self.parts = parts
        self.total_oz = None
        self.total_parts = None
    @property
    def oz(self):
      return self.total_oz * (self.parts * 1./self.total_parts)
    @property
    def json(self):
        return {'parts': self.parts}


class Drops(Unit):
    def __init__(self, drops):
        self.drops = drops
    @property
    def oz(self):
        return 0
    def __str__(self):
        return "%i drops" % self.drops
    @property
    def parts(self):
        return 0
    @property
    def json(self):
        return {'drops': self.drops}

