'''use regex and spacy to detect mentions in a text'''

import sys
import os
import json
import random
import spacy
from spacy.util import minibatch, compounding
from spacy.scorer import Scorer
from spacy.gold import GoldParse
from spacy.tokens import DocBin
from spacy.training.example import Example
from spacy.tokens import Doc
from spacy.vocab import Vocab
from spacy.training import Example
import re


class DetectMention:
    '''use regex and spacy to detect mentions in a text'''

    def __init__(self):
        '''class constructor'''
        pass

    def detect(self, json_data):
        '''use regex and spacy to detect mentions in a text'''

        print('detect mention')

        # load the trained NLP model
        nlp = spacy.load('en_core_web_sm')

        # create a Doc object
        doc = nlp(json_data['text'])

        # find all mentions of the entity
        mentions = re.findall(json_data['entity'], json_data['text'])

        # for each mention, create a span
        for mention in mentions:
            span = doc.char_span(mention.start(), mention.end(), label='DIRECT_MENTION')
            if span is not None:
                # create a new entity in the Doc
                doc.ents = list(doc.ents) + [span]

        # create a list of entities
        entities = []
        for ent in doc.ents:
            entities.append(ent.text)

        # return the entities
        return entities