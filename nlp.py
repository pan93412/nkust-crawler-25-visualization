from collections import Counter
import functools
from glob import glob
import json
import hanlp
import hanlp.pretrained
import wordcloud

import cleaner


class Nlp:
    def __init__(self):
        self.cleaner = cleaner.BasicCleaner()
        self.segmenter = hanlp.load(hanlp.pretrained.tok.COARSE_ELECTRA_SMALL_ZH)

    @functools.cached_property
    def stopwords(self) -> set[str]:
        stopwords = set()
        for path in glob("./stopwords/*.json"):
            with open(path, "r") as f:
                stopwords.update(json.load(f))
        return stopwords

    def segment(self, text: str) -> list[str]:
        normalized_text = self.cleaner.clean_text(text)
        segmented = self.segmenter(normalized_text)
        return [word for word in segmented if word not in self.stopwords]

    def word_count(self, text: str) -> dict[str, int]:
        words = self.segment(text)
        return Counter(words)

    def word_cloud(self, word_counts: dict[str, int]) -> str:
        wc = wordcloud.WordCloud(
            font_path="./fonts/arial-unicode.ttf",
            width=1024,
            height=768,
            random_state=42,
        )
        wc.generate_from_frequencies(word_counts)

        return wc.to_svg(embed_font=True)
