#!/usr/bin/env python3
import argparse
import re
import sys

import spacy


def main(args):
    nlp = spacy.load(args.spacy_model, disable=["parser", "ner", "textcat"])
    for line in sys.stdin:
        tokenized_text = line.strip()
        n_tokens = len(tokenized_text.split())
        full_text = re.sub(r" ##([^\s])", r"\1", tokenized_text)
        doc = nlp(full_text)
        tags = []
        for i, token in enumerate(doc):
            if token.text == "SEP":
                # [SEP] instance (previous token was '[')
                # Change last tag
                tags[-1] = "SPECIAL_TOKEN"
            elif i == 0:
                # Beginning of sentence, pos tag is valid
                pos_tag = token.pos_
                tags.append(f"B-{pos_tag}")
            elif tokenized_text[0] == " " and tokenized_text[1:3] != "##":
                # End of word, pos tag is valud
                pos_tag = token.pos_
                tags.append(f"B-{pos_tag}")
                tokenized_text = tokenized_text[1:]

            for char in token.text:
                if char == tokenized_text[0]:
                    # char is the first from tokenized_text, move on 
                    tokenized_text = tokenized_text[1:]
                elif tokenized_text[:3] == " ##":
                    # tokenized_text starts with ` ##`, append I(nside) tag
                    assert(char == tokenized_text[3])
                    tokenized_text = tokenized_text[4:]
                    tags.append(f"I-{pos_tag}")
        assert(len(tags) == n_tokens)
        print(args.delimiter.join(tags))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract POS tags using SpaCy."
                    "Reads stdin, writes to stdout.")
    parser.add_argument("spacy_model")
    parser.add_argument("-d", "--delimiter", default=",")
    main(parser.parse_args())
