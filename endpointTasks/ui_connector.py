'''class that sends a proactive card to microsoft teams'''
'''
In order to send actionable messages one must use the legacy message card. Here is the documentation:
https://learn.microsoft.com/en-us/outlook/actionable-messages/message-card-reference
'''

import requests
from json import load, dumps
import os

class UsersConnector:
    '''class that sends a proactive card to microsoft teams'''

    def __init__(self, media_house: str, text: str):
        assert media_house in ['MDR', 'BR'], 'media_house must be MDR or BR'
        self.media_house = media_house
        self.text = text

    def send_msteams_notification(self):
        '''sends the message'''
        headers = {
            'Content-type': 'application/json',
        }
        with open(os.path.join(os.path.dirname(__file__), '..', '.credentials', 'webhooks.json')) as json_file:
            webhook_url = load(json_file)[self.media_house]

        data = {
            "@type": "MessageCard",
            "@context": "http://schema.org/extensions",
            "summary": "Feedback",
            "title": "New direct mention was detected:",
            "text": self.text,
            "potentialAction": [
                {
                    "@type": "ActionCard",
                    "name": "Feedback",
                    "inputs": [
                        {
                            "@type": "MultichoiceInput",
                            "id": "HumanLabel",
                            "title": "In order to improve the detection, please give us feedback about the detection:",
                            "isMultiSelect": "False",
                            "style": "expanded",
                            "choices": [
                                {
                                    "display": "There is a direct mention and the exact text is bolded.",
                                    "value": "correct"
                                },
                                {
                                    "display": "There is not direct mention at all.",
                                    "value": "incorrect"
                                },
                                {
                                    "display": "There is a direct mention but the exact text is not bolded.",
                                    "value": "incorrect_bold"
                                }
                            ]
                        },
                        {
                            "@type": "TextInput",
                            "id": "mentionText",
                            "isMultiline": True,
                            "title": "exact mention text"
                        }
                    ],
                    "actions": [
                        {
                            "@type": "HttpPOST",
                            "name": "Submit",
                            "isPrimary": True,
                            "target": "https://webhook.site/9d6c4c4d-8d3a-4f2a-8d5b-8e6a9e6b22c6"
                        }
                    ]
                }
            ]
        }

        response = requests.post(self.webhook_url, headers=headers, data=dumps(data))

'''
if __name__ == '__main__':
    
    feedback = UsersConnector('MDR', 'This is a comment that contains **some bolded direct mention**. Lets continue testing')
    feedback.send_msteams_notification()
'''