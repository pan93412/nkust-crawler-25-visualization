from collections import Counter
import functools
from glob import glob
import json
import string
import hanlp
import hanlp.pretrained
import wordcloud

import cleaner

# https://hanlp.hankcs.com/docs/annotations/pos/ctb.html
ACCEPTED_POS = [
    "CD",
    "FW",
    "JJ",
    "NN",
    "NR",
    "NT",
    "OD",
    "VA",
    "VV"
]

class Nlp:
    def __init__(self):
        self.cleaner = cleaner.BasicCleaner()
        self.segmenter = hanlp.load(hanlp.pretrained.tok.COARSE_ELECTRA_SMALL_ZH)
        self.pos_tagger = hanlp.load(hanlp.pretrained.pos.CTB9_POS_ELECTRA_SMALL)

    @functools.cached_property
    def stopwords(self) -> set[str]:
        stopwords = set()
        for path in glob("./stopwords/*.json"):
            with open(path, "r") as f:
                stopwords.update(json.load(f))

        stopwords.update(string.punctuation + string.whitespace)

        return stopwords

    def segment(self, text: str) -> list[str]:
        normalized_text = self.cleaner.clean_text(text)
        segmented = self.segmenter(normalized_text)

        # filter out stopwords
        segmented_cleaned = [word for word in segmented if word not in self.stopwords]

        # tag pos
        pos = self.pos_tagger(segmented_cleaned)

        # filter out words that are not in the accepted pos
        return [word for word, p in zip(segmented_cleaned, pos) if p in ACCEPTED_POS]

    def word_count(self, text: str) -> dict[str, int]:
        words = self.segment(text)
        return Counter(words)

    def keywords(self, word_counts: dict[str, int]) -> list[str]:
        # find the most 5 frequent words
        most_frequent_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        return [word for word, _ in most_frequent_words]

    def word_cloud(self, word_counts: dict[str, int]) -> str:
        wc = wordcloud.WordCloud(
            font_path="./fonts/arial-unicode.ttf",
            width=1024,
            height=768,
            random_state=42,
        )
        wc.generate_from_frequencies(word_counts)

        return wc.to_svg(embed_font=True)
