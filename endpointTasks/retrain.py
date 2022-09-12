'''trains an NLP classifier to detect direct mentions of a given entity in a given text'''

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

class TrainDirectMentionModel:
    '''trains an NLP classifier to detect direct mentions of a given entity in a given text'''

    def __init__(self):
        '''class constructor'''
        pass

    def train(self, json_data):
        '''trains an NLP classifier to detect direct mentions of a given entity in a given text'''

        print('train direct mention model')

        # create a blank NLP model
        nlp = spacy.blank('en')

        # create a blank entity recognizer and add it to the pipeline
        ner = nlp.create_pipe('ner')
        nlp.add_pipe(ner, last=True)

        # add the entity label to the entity recognizer
        ner.add_label('DIRECT_MENTION')

        # get names of other pipes to disable them during training
        other_pipes = [pipe for pipe in nlp.pipe_names if pipe != 'ner']

        # only train NER
        with nlp.disable_pipes(*other_pipes):

            # reset and initialize the weights randomly – but only if we're
            # training a new model
            nlp.begin_training()

            # train for 30 iterations
            for itn in range(30):

                # shuffle the training data
                random.shuffle(json_data)

                # batch up the examples using spaCy's minibatch
                batches = minibatch(json_data, size=compounding(4.0, 32.0, 1.001))
                losses = {}

                # iterate through minibatches
                for batch in batches:
                    for text, annotations in batch:

                        # create Example
                        doc = nlp.make_doc(text)
                        example = Example.from_dict(doc, annotations)

                        # update the model
                        nlp.update([example], losses=losses, drop=0.5)

                print('Losses', losses)

        # save model to output directory
        if not os.path.exists('output'):
            os.makedirs('output')

        nlp.to_disk('output')

        print('model saved')