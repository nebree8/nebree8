"""Actions break up the process of making a drink into smaller pieces.

They are callables with an optional inspect method."""


class Action(object):
  """Actions processed by the Controller to make drinks."""

  def __call__(self, robot):
    raise NotImplementedError()

  def sensitive(self):
    return False

  def inspect(self):
    """Returns a description of this action."""
    return {'name': self.__class__.__name__, 'args': self.__dict__}

  def __str__(self):
    args = sorted('%s=%s' % i for i in self.__dict__.iteritems())
    if sum(len(s) for s in args) < 80:
      args = ' ' + ' '.join(args)
    else:
      args = '\n\t' + '\n\t'.join(s.replace('\n', '\n\t') for s in args)
    return '%s: %s' % (self.__class__.__name__, args)


class ActionException(Exception):
  pass
