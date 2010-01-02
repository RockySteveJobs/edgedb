class NaturalLanguageObject(object):
    pass


class GrammaticalCategoryMeta(type):
    index = {}

    def __init__(cls, name, bases, dct):
        super(GrammaticalCategoryMeta, cls).__init__(name, bases, dct)

        name = dct.get('name')
        if name:
            idx = GrammaticalCategoryMeta.index
            if name in idx:
                raise Exception('Grammatical category "%s" is already used by %s.%s' %
                                (name, idx[name].__module__, idx[name].__name__))
            else:
                idx[name] = cls
        else:
            raise Exception('Missing required grammatical category name')


def is_valid_category(category):
    return category in GrammaticalCategoryMeta.index


def form(category, value):
    cls = GrammaticalCategoryMeta.index.get(category)
    if cls:
        return cls(value)
    else:
        raise Exception('reference to an invalid grammatical category: %s' % category)


class GrammaticalCategory(object, metaclass=GrammaticalCategoryMeta):
    name = 'category'

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value

    def __repr__(self):
        return '<%s %r>' % (self.__class__.name, self.value)

    def __eq__(self, other):
        if isinstance(other, GrammaticalCategory):
            return self.value == other.value
        elif isinstance(other, str):
            return self.value == other
        else:
            return False

    def __hash__(self):
        return hash(self.__class__.name + ':' + self.value)


class GrammaticalNumber(GrammaticalCategory):
    name = 'number'

    def format_count(self, count):
        pass


class Singular(GrammaticalNumber):
    name = 'singular'


class Plural(GrammaticalNumber):
    name = 'plural'


class WordCombination(NaturalLanguageObject):
    def __init__(self, value):
        if isinstance(value, str):
            value = {Singular(value)}

        self.forms = {}

        for form in value:
            self.forms[form.__class__.name] = form

        self.value = self.forms.get('singular')
        if not self.value:
            self.value = next(iter(self.forms.values()))

    def __getattr__(self, attribute):
        value = self.forms.get(attribute)

        if not value:
            raise AttributeError('%s is not defined for %r' % (attribute, self))

        return value

    def as_dict(self):
        return self.forms

    @classmethod
    def from_dict(cls, dct):
        forms = set()

        for key, value in dct.items():
            forms.add(form(key, value))
        return cls(forms)

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return '<%s %r>' % (self.__class__.__name__, self.value)

    def __eq__(self, other):
        if isinstance(other, WordCombination):
            return self.forms == other.forms
        elif isinstance(other, str):
            return self.value == other
        else:
            return False

    def __hash__(self):
        return hash(self.forms)
