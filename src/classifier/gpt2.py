from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    AutoConfig,
    pipeline,
)

from settings import GPT2_MODEL_PATH
from src.classifier.preprocess import preprocess_comment_text


class GPT2:
    def __init__(self, model_path: str = GPT2_MODEL_PATH) -> None:
        """Initialise model.

        :param model_path: path to the model source files
        """
        self._model_path = model_path
        self._tokenizer = AutoTokenizer.from_pretrained(self._model_path)
        self._tokenizer.pad_token = self._tokenizer.eos_token
        self._model = AutoModelForSequenceClassification.from_pretrained(
            self._model_path
        )
        self._pipe = pipeline(
            "text-classification", model=self._model, tokenizer=self._tokenizer
        )

    def classify(self, text: str, preprocess_text: bool = True) -> bool:
        """True, if text contains mentions, false otherwise.

        :param text: text to classify
        :param preprocess_text: preprocess text before training, if true
        """
        if preprocess_text:
            try:
                text = preprocess_comment_text(text)
            except (ValueError, TypeError):
                return False

        result = self._pipe(text)
        label = result[0]["label"]
        if label == "LABEL_1":
            return True
        elif label == "LABEL_0":
            return False
        else:
            raise ValueError(f"Got unknown classification label: {label}")

    __call__ = classify
