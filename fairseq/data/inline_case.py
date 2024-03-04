import re
import sys

import pyonmttok

upper_case_mark = "〈"
title_case_mark = "〉"

tokenizer = pyonmttok.Tokenizer("aggressive", segment_case=True, joiner_annotate=True, joiner_new=False, joiner='■')


def add_inline_casing(tokens):
    # add prefix token with "%t" if title case
    # add prefix token with "%u" if uppercase
    # lowercase the token
    # e.g ["This", "is", "a", "TEXT"] -> ["%t", "this", "is", "a", "%u", "text"]

    new_tokens = []
    for index, token in enumerate(tokens):
        type = None
        if token.isupper():
            if len(token) == 1:
                type = 'title'
            else:
                type = 'upper'

        elif token.istitle():
            type = 'title'

        if type == 'upper':
            token = upper_case_mark + " " + token
        elif type == 'title':
            token = title_case_mark + " " + token

        new_tokens.append(token.lower())
    return new_tokens


def restore_case(tokens):
    # restore case
    # e.g. ["%t", "this", "is", "a", "%u", "test"] -> ["This", "is", "a", "Test"]
    new_tokens = []
    index = 0
    while index < len(tokens):
        token = tokens[index]
        next_token = tokens[index + 1] if index < len(tokens) - 1 else ""
        if upper_case_mark in token:
            to_add = next_token.upper()
            new_tokens.append(to_add)
            index += 1
        elif title_case_mark in token:
            to_add = next_token.title()
            new_tokens.append(to_add)
            index += 1
        else:
            new_tokens.append(token)
        index += 1

    return new_tokens


def do_tok(line):
    line = line.strip()
    line = re.sub(r'\s+', ' ', line)
    tokens = tokenizer(line)
    tokens = add_inline_casing(tokens)
    # print(tokens)
    joined_line = " ".join(tokens)
    return joined_line


def do_detok(line):
    line = re.sub(r'\s+', ' ', line)
    new_tokens = line.split(" ")
    tokens_restored = restore_case(new_tokens)
    # print(tokens)
    detok = tokenizer.detokenize(tokens_restored)
    return detok


if __name__ == "__main__":
    with open('test_lines.txt', 'r') as f, open('test_lines.toked.txt', 'w') as f_tok, open('test_lines.detoked.txt', 'w') as f_detok:
        lines = f.readlines()
        lines = [line.strip() for line in lines]
        # lines = ["Tournez le boutonTemps/Poids"]
        # lines = [
        #     "Le poids de dEF1 est COMPRIS entre 100 et 1500 g, et le temps de DEF2 est compris entre 0:10 et 60:00 boutonTemps/Poids.",
        #     "RAYONNEMENT DES MICRO-ONDES",
        #     "https://sds.diversey.com/?guiLang=FR",
        #     "Tournez le boutonTemps/Poids"
        # ]
        for line in lines:
            line = re.sub(r'\s+', ' ', line)
            tokens = tokenizer(line)
            tokens = add_inline_casing(tokens)
            # print(tokens)
            joined_line = " ".join(tokens)
            f_tok.write(joined_line + "\n")
            # print(joined_line)
            new_tokens = joined_line.split(" ")
            tokens_restored = restore_case(new_tokens)
            # print(tokens)
            detok = tokenizer.detokenize(tokens_restored)
            same = line == detok
            f_detok.write(detok + "\n")
            # print("----------------")
            if not same:
                print("ERROR-----------------------------")
                print("line ", line)
                print("tokens   ", tokens)
                print("joined_line  ", joined_line)
                print("new_tokens   ", new_tokens)
                print("detok        ", detok)
