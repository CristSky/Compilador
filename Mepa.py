__author__ = 'Claudio Costa'
# -*- coding: utf-8 -*-
# !/usr/bin/env python

import collections
import re
from collections import deque


###############################################################################
class Lex():
    def __init__(self, statements=None):
        self.Token = collections.namedtuple('Token', ['typ', 'value', 'line', 'column'])
        if statements:
            self.tokenize(statements)

    def tokenize(self, code):
        list = []
        keywords = {'PROGRAM', 'VAR', 'INTEGER', 'WHILE', 'BEGIN', 'END', 'IF', 'THEN', 'ELSE', 'READ'}
        token_specification = [
            ('COMMENT', r'(?://[A-Za-z0-9_]+\n)|(#.*?\n)'),  # comentario com // ou #
            ('NUMBER', r'\d+(\.\d*)?'),  # Integer or decimal number
            ('ASSIGN', r':='),  # Assignment operator
            ('END', r';'),  # Statement terminator
            ('ID', r'[A-Za-z0-9_]+'),  # Identifiers
            ('OP', r'[+\-*/%]'),  # Arithmetic operators
            ('NEWLINE', r'\n'),  # Line endings
            ('SKIP', r'[ \t\r\n]+'),  # Skip over spaces and tabs
            ('MISMATCH', r'./'),  # Any other character
            ('STRING', r'(".*?")'),
            ('SPECIAL', r'[<>(){}.,\[\]]'),
        ]
        tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
        line_num = 1
        line_start = 0
        for mo in re.finditer(tok_regex, code):
            kind = mo.lastgroup
            value = mo.group(kind)
            if kind == 'NEWLINE' or kind == 'COMMENT':
                line_start = mo.end()
                line_num += 1
            elif kind == 'SKIP':
                pass
            elif kind == 'MISMATCH':
                raise RuntimeError('%r unexpected on line %d' % (value, line_num))
            else:
                if kind == 'ID' and value in keywords:
                    kind = value
                column = mo.start() - line_start
                list.append(self.Token(kind, value, line_num, column))
                # yield self.Token(kind, value, line_num, column)
        return list

    """
    tokens = deque()
    tipos = deque()
    for token in tokenize():
        tipos.append(token.typ)
        tokens.append(token.value)
    tokens.append('$')

    print(tokens)
    print(tipos)
    """


###############################################################################
class Translator():
    def __init__(self):
        self.var = {}
        self.code = []
        self.tok = None
        self.text = ""

    def translate(self, tokens):
        i = 0
        self.tokens = tokens
        size = len(tokens)
        while i < size:
            if self.tokens[i].typ == "PROGRAM":
                self.INPP()
            elif self.tokens[i].typ == 'VAR':
                i = self.AMEM(i + 1)
            elif self.tokens[i].typ == 'READ':
                self.LEIT(i + 2)
                i += 4
            elif self.tokens[i].typ == 'ID':

                pass


            i += 1

        ######################
        for line in self.code:
            self.text += line
        return self.text

    def INPP(self):
        self.code.append("INPP\n")

    def AMEM(self, index):
        i = index
        count = 0
        while self.tokens[i].typ != 'BEGIN':
            if self.tokens[i].typ == 'ID':
                self.var[self.tokens[i].value] = 0
                count += 1
            i += 1
        self.code.append('AMEM ' + str(count) + "\n")
        return i

    def LEIT(self, index):
        self.code.append("LEIT\n")
        self.code.append("ARMZ " + self.tokens[index].value + '\n')


###############################################################################
class Mepa():
    def __init__(self):
        self.S = 0  # Ponteiro da pilha M
        self.I = 0  # Contador de programs
        self.D = []  # registrador aux
        self.M = []  # memoria
        self.P = []  # programa

    def CRCT(self, const):
        self.M.append(const)
        # self.S += 1


###############################################################################
if __name__ == "__main__":
    f = open("pascal.c", "r")
    code = f.read()
    f.close()
    ###################
    lexico = Lex()
    tradutor = Translator()
    mepa = Mepa()
    toke = lexico.tokenize(code)

    mepa.CRCT(9)

    texto = tradutor.translate(toke)
    print(texto)

    arq = open("traducao.txt", "w")
    arq.writelines(texto)
    arq.close()

"""
PROGRAM TESTE;
	VAR N, K : INTEGER;
	VAR F1, F2, F3 : INTEGER;
BEGIN
	READ(N);
	F1:=0;
	F2:=1;
	K:=1;

	WHILE K <= N DO
	BEGIN
		F3 := F1 + F2;
		F1 := F2;
		F2 := F3;
		K := K + 1;
	END;

	WRITE(N, F1);
END;
"""
