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
            ('ENDLINE', r';'),  # Statement terminator
            ('ID', r'[A-Za-z0-9_]+'),  # Identifiers
            ('OP', r'[+\-*/%]'),  # Arithmetic operators
            ('NEWLINE', r'\n'),  # Line endings
            ('SKIP', r'[ \t\r\n]+'),  # Skip over spaces and tabs
            ('MISMATCH', r'./'),  # Any other character
            ('STRING', r'(".*?")'),
            ('SPECIAL', r'[<>(){}.,\[\]]='),
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


#########################  TRANSLATOR  ######################################################
class Translator():
    def __init__(self):
        self.var = {}
        self.code = []
        self.tok = None
        self.text = ""

    def translate(self, tokens, int):
        i = int
        self.tokens = tokens
        size = len(tokens)
        while i < size:
            if self.tokens[i].typ == "PROGRAM":
                self.INPP()
            elif self.tokens[i].typ == 'VAR':
                i = self.AMEM(i + 1)
            elif self.tokens[i].typ == 'READ':
                self.LEIT(i)
                i += 2
            elif (self.tokens[i].typ == 'ID'):
                if(self.tokens[i+1].typ == 'ASSIGN') and (self.tokens[i+2].typ == 'NUMBER') and (self.tokens[i+3].typ == 'ENDLINE'):
                    self.CRCTI(i)
                    i += 3
                elif(self.tokens[i+1].typ == 'ASSIGN') and (self.tokens[i+2].typ == 'ID') and (self.tokens[i+3].typ == 'ENDLINE'):
                    self.CRVL(i+2)
                    self.ARMZ(i)
            #todo


            elif self.tokens[i].typ == 'WHILE':
                self.NADA(tokens, i)
                i += 1
                self.CRVL(i)
                i += 1
                self.CRVL(i+1)
                if self.tokens[i].value == '<=':
                    self.CompOp(tokens[i].value)
                i += 4
                aux = i
                self.DSVF(i)
                self.translate(tokens, i)



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
        self.ARMZ(index+1)

    def CRCTI(self, index):
        self.code.append("CRTC " + self.tokens[index+2].value + '\n')
        self.code.append("ARMZ " + self.tokens[index].value + '\n')

    def CRVL(self, index):
        self.code.append("CRVL " + self.tokens[index].value + '\n')

    def ARMZ(self, index):
        self.code.append("ARMZ " + self.tokens[index].value + '\n')

    def CMME(self):
        self.code.append("CMME \n")
    def CMMA(self):
        self.code.append("CMMA \n")
    def CMIG(self):
        self.code.append("CMIG \n")
    def CMDG(self):
        self.code.append("CMDG \n")
    def CMEG(self):
        self.code.append("CMEG \n")
    def CMAG(self):
        self.code.append("CMAG \n")
    def DSVF(self,index):
        self.code.append("DSVF L" + str(index) + '\n')

    def NADA(self, toke, index):
        aux = index
        self.code.append("L" + str(index) + "  NADA\n")

    def CompOp(self, op):
        if op == '<':
            self.CMME()
        elif op == '>':
            self.CMMA()
        elif op == '==':
            self.CMIG()
        elif op == '!=':
            self.CMDG()
        elif op == '<=':
            self.CMEG()
        elif op == '>=':
            self.CMAG()

##############################    MEPA     #################################################
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

    texto = tradutor.translate(toke, 0)
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
