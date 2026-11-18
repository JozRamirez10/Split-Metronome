import collections
import collections.abc

def apply_madmom_patch():
    """Inject the obsolete collection classes so that madmom can compile"""
    collections.MutableSequence = collections.abc.MutableSequence
    collections.Mapping = collections.abc.Mapping
    collections.MutableMapping = collections.abc.MutableMapping
    collections.Iterable = collections.abc.Iterable
    collections.Sequence = collections.abc.Sequence
    collections.Callable = collections.abc.Callable