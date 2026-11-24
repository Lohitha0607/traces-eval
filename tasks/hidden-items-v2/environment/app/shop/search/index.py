"""A small inverted index: word -> set of keys."""
from collections import defaultdict

from shop.utils.text import tokenize


class SearchIndex:
    def __init__(self):
        self._postings = defaultdict(set)

    def add(self, key, text):
        for word in tokenize(text):
            self._postings[word].add(key)

    def query(self, text):
        words = tokenize(text)
        if not words:
            return set()
        result = set(self._postings.get(words[0], set()))
        for word in words[1:]:
            result &= self._postings.get(word, set())
        return result
