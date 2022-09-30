'''trains an NLP classifier to detect direct mentions of a given entity in a given text'''
# I would like to give credit to the following article for the code in this file:
# https://www.machinelearningplus.com/nlp/training-custom-ner-model-in-spacy/

# in this first version I make use of the pre-trained german model:
# python -m spacy download de_core_news_sm

import os
import json
import random
import spacy
from spacy.util import minibatch, compounding
from spacy.training.example import Example
from spacy.training import Example
from spacy.scorer import Scorer

class TrainDirectMentionModel:
    '''trains an NLP classifier to detect direct mentions in a given text'''

    def __init__(self):
        '''class constructor'''
        pass

    def load_prodigy_data(self):
        '''load training data contained in the data/ directory'''

        training_data = []
        for filename in os.listdir(os.path.abspath('.') + '/data/prodigy'):
            with open('data/' + filename, 'r', encoding='utf-8') as f:
                for line in f:
                    training_data.append(json.loads(line.rstrip('\n|\r')))

        # return a list of tuples containing the text and the annotations if the "spans" key exists
        data = [(x['text'], {'entities': [(y['start'], y['end'], y['label']) for y in x['spans']]}) for x in training_data if 'spans' in x]
        return data

    def split_data(self, data, split=80):
        '''shuffles and splits the data in a train and test set based on the split proportion in percent'''
        random.shuffle(data)
        idx = int(len(data)/100 * split)
        train_data = data[:idx]
        test_data = data[idx:]
        return train_data, test_data


    def train(self, train_data):
        '''trains an NLP classifier to detect direct mentions of a given entity in a given text'''

        nlp = spacy.load('de_core_news_sm')

        ner = nlp.get_pipe("ner")

        for _, annotations in train_data:
            for ent in annotations.get("entities"):
                ner.add_label(ent[2])

        # disable other pipes
        pipe_exceptions = ["ner", "trf_wordpiecer", "trf_tok2vec"]
        unaffected_pipes = [pipe for pipe in nlp.pipe_names if pipe not in pipe_exceptions]

        with nlp.disable_pipes(*unaffected_pipes):

            # Training for 30 iterations
            for iteration in range(50):

                losses = {}
                # batch up the examples using spaCy's minibatch
                batches = minibatch(train_data, size=compounding(4.0, 32.0, 1.001))
                for batch in batches:
                    texts, annotations = zip(*batch)
                    example = []
                    # Update the model with iterating each text
                    for i in range(len(texts)):
                        doc = nlp.make_doc(texts[i])
                        example.append(Example.from_dict(doc, annotations[i]))

                    # Update the model
                    nlp.update(example, drop=0.5, losses=losses)

        # save model to output directory

        nlp.to_disk(os.path.abspath('.') + '/models/detect_mentions')

        print('model saved')

    def predict(self, model, text):
        '''predicts the entities in a given text'''

        doc = model(text)

        predictions = []
        print(text)
        for ent in doc.ents:
            p = (ent.text, {'entities': [(ent.start, ent.end, 'MENTION')]})

            predictions.append(p)
            print(p)

        return predictions

    def evaluate_predictions(self, model, test_data):        
        # test_data = [('MDR lebt einfach damit das ihr und die Politiker Widerspruch kriegen.', {'entities': [(0, 3, 'MENTION')]})]
        examples = []
        for text, annots in test_data:
            doc = model.make_doc(text)
            examples.append(Example.from_dict(doc, annots))

        print(examples)

    def score_predictions(self, model, test_data):
        scorer = Scorer()
        examples = []
        for text, annotations in test_data:
            doc = model.make_doc(text)
            example = Example.from_dict(doc, annotations)
            example.predicted = model(str(example.predicted))
            examples.append(example)
        scorer.score(examples)

        print(scorer.score(examples))

if __name__ == '__main__':

    # create an instance of the class
    trainDirectMentionModel = TrainDirectMentionModel()

    # load the training data
    json_data = trainDirectMentionModel.load_data()

    # split the data
    train_data, test_data = trainDirectMentionModel.split_data(json_data, split=80)

    # train the model
    # trainDirectMentionModel.train(train_data)

    # load the model
    direct_mention_model = spacy.load('./models/detect_mentions')

    # check the predictions
    # trainDirectMentionModel.evaluate_predictions(direct_mention_model, test_data)

    trainDirectMentionModel.score_predictions(direct_mention_model, test_data)
