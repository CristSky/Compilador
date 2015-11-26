__author__ = 'Claudio Costa'
# -*- coding: utf-8 -*-
# !/usr/bin/env python

import collections
import re
from collections import deque


#################################      LEXICO    ##############################################
class Lex():
    def __init__(self, statements=None):
        self.Token = collections.namedtuple('Token', ['typ', 'value', 'line', 'column'])
        if statements:
            self.tokenize(statements)

    def tokenize(self, code):
        list = []
        keywords = {'PROGRAM', 'VAR', 'INTEGER', 'WHILE', 'BEGIN', 'END', 'IF', 'THEN', 'ELSE', 'READ', 'WRITE'}
        token_specification = [
            ('COMMENT', r'(?://[A-Za-z0-9_]+\n)|(#.*?\n)'),  # comentario com // ou #
            ('NUMBER', r'\d+(\.\d*)?'),  # Integer or decimal number
            ('ABPAR', r'\('),  # Abre Parenteses
            ('FEPAR', r'\)'),  # fecha Parenteses
            ('MEIG', r'<='),  # menor igual
            ('MAIG', r'>='),  # maior igual
            ('ME', r'<'),  # menor
            ('MA', r'>'),  # maior
            ('DI', r'!='),  # diferente
            ('IG', r'=='),  # igual
            ('VIR', r'\,'),  # virgula
            ('ASSIGN', r':='),  # Assignment operator
            ('ENDLINE', r';'),  # Statement terminator
            ('ID', r'[A-Za-z0-9_]+'),  # Identifiers
            ('OP', r'[+\-*/%]'),  # Arithmetic operators
            ('NEWLINE', r'\n'),  # Line endings
            ('SKIP', r'[ \t\r\n]+'),  # Skip over spaces and tabs
            ('MISMATCH', r'./'),  # Any other character
            ('STRING', r'(".*?")'),
            ('SPECIAL', r'[<>{}.\[\]]\='),
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
        self.qtdevar = 0

    def translate(self, tokens, start, end):
        i = start
        e = end

        self.tokens = tokens
        size = len(tokens)
        while (i < size):
            if (i == e):
                break
            if self.tokens[i].typ == "PROGRAM":
                self.INPP()
                i = self.counter(tokens, i)
            elif self.tokens[i].typ == 'VAR':
                i = self.AMEM(i + 1)
            elif self.tokens[i].typ == 'READ':
                i += 2
                while (tokens[i].typ != 'FEPAR'):
                    self.LEIT(i)
                    i += 1
                    if (tokens[i].typ == 'VIR'):
                        i += 1

                i += 1
            elif self.tokens[i].typ == 'WRITE':
                i += 2
                aux = i
                con = 0

                while self.tokens[aux].value != ';':
                    if self.tokens[aux].value == ',':
                        con += 1
                    aux += 1
                z = 0

                while z <= con:
                    if (tokens[i].typ == 'ID') and ((tokens[i + 1].typ == 'VIR') or (tokens[i + 1].typ == 'FEPAR')):
                        self.CRVL(i)
                        i += 2
                    elif (tokens[i].typ == 'NUMBER') and (
                        (tokens[i + 1].typ == 'VIR') or (tokens[i + 1].typ == 'FEPAR')):
                        self.CRCTI(i)
                        i += 2
                    elif (tokens[i + 1].typ == 'OP'):
                        self.NotPolonesa(tokens, i)
                        while (tokens[i].typ != 'VIR') and (tokens[i].typ != 'FEPAR'):
                            i += 1
                        i += 1
                    self.IMPR()

                    z += 1

            elif self.tokens[i].typ == 'ID':
                if (self.tokens[i + 1].typ == 'ASSIGN') and (self.tokens[i + 2].typ == 'NUMBER') and (
                    self.tokens[i + 3].typ == 'ENDLINE'):
                    self.CRCTI(i + 2)
                    self.ARMZ(i)
                    i += 3
                elif (self.tokens[i + 1].typ == 'ASSIGN') and (self.tokens[i + 2].typ == 'ID') and (
                    self.tokens[i + 3].typ == 'ENDLINE'):
                    self.CRVL(i + 2)
                    self.ARMZ(i)
                    i += 3
                elif (self.tokens[i + 1].typ == 'ASSIGN'):
                    self.NotPolonesa(tokens, i + 2)
                    self.ARMZ(i)
                    i = self.counter(tokens, i)
                elif (self.tokens[i + 1].typ == 'OP'):
                    self.NotPolonesa(tokens, i)
                    i = self.counter(tokens, i)
                else:
                    self.CRVL(i)

            # todo if
            elif self.tokens[i].typ == 'IF':
                int1 = i
                i += 1
                while self.tokens[i].typ != 'THEN':
                    if (self.tokens[i].typ == 'ID') and (self.tokens[i + 2].typ == 'ID'):
                        self.CRVL(i)
                        self.CRVL(i + 2)
                        i += 1
                    elif (self.tokens[i].typ == 'ID') and (self.tokens[i + 2].typ == 'NUMBER'):
                        self.CRVL(i)
                        self.CRCTI(i + 2)
                        i += 1
                    elif (self.tokens[i].typ == 'NUMBER') and (self.tokens[i + 2].typ == 'ID'):
                        self.CRCTI(i)
                        self.CRVL(i + 2)
                        i += 1
                    elif (self.tokens[i].typ == 'NUMBER') and (self.tokens[i + 2].typ == 'NUMBER'):
                        self.CRCTI(i)
                        self.CRCTI(i + 2)
                        i += 1
                    elif (self.tokens[i].typ == 'MEIG') or (self.tokens[i].typ == 'MAIG') or (
                        self.tokens[i].typ == 'IG') or (self.tokens[i].typ == 'DI') or (self.tokens[i].typ == 'ME') or (
                        self.tokens[i].typ == 'MA'):
                        self.CompOp(tokens[i].value)
                        i += 2
                        self.DSVF(int1)
                # pega o index do else
                aux = i
                while tokens[aux].typ != 'ELSE':
                    aux += 1
                self.translate(tokens, i, aux)
                i = aux
                self.DSVS(aux)
                self.NADA(int1)
                tmp = i
                while tokens[tmp].typ != 'END':
                    tmp += 1
                self.translate(tokens, i, tmp)
                i = tmp
                self.NADA(aux)



            elif self.tokens[i].typ == 'WHILE':
                self.NADA(i)
                back = i
                i += 1
                self.CRVL(i)
                i += 1
                self.CRVL(i + 1)
                if (self.tokens[i].typ == 'MEIG') or (self.tokens[i].typ == 'MAIG') or (self.tokens[i].typ == 'IG') or (
                    self.tokens[i].typ == 'DI') or (self.tokens[i].typ == 'ME') or (self.tokens[i].typ == 'MA'):
                    self.CompOp(tokens[i].value)
                i += 4
                tmp = i
                stop = 1
                # Verifica para onde o while acaba
                while stop != 0:
                    if tokens[tmp].typ == 'WHILE':
                        stop += 1
                    elif tokens[tmp].typ == 'END':
                        stop -= 1
                    else:
                        tmp += 1

                aux = i
                self.DSVF(i)
                self.translate(tokens, i, tmp)
                self.DSVS(back)
                self.NADA(aux)
                i = tmp

            i += 1

        if i == len(tokens):
            self.DMEM()
            for line in self.code:
                self.text += line

            self.text += 'PARA'
            return self.text

    def INPP(self):
        self.code.append("INPP\n")

    def AMEM(self, index):
        i = index
        count = 0
        while self.tokens[i].typ != 'BEGIN':
            if self.tokens[i].typ == 'ID':
                self.var[self.tokens[i].value] = 0
                self.qtdevar += 1
            i += 1
        self.code.append('AMEM ' + str(self.qtdevar) + "\n")
        return i

    def DMEM(self):
        self.code.append('DMEM ' + str(self.qtdevar) + "\n")

    def LEIT(self, index):
        self.code.append("LEIT \n")
        self.ARMZ(index)

    def IMPR(self):
        self.code.append("IMPR \n")

    def CRCTI(self, index):
        self.code.append("CRTC " + self.tokens[index].value + '\n')

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

    def DSVF(self, index):
        self.code.append("DSVF L" + str(index) + '\n')

    def DSVS(self, index):
        self.code.append("DSVS L" + str(index) + '\n')

    def NADA(self, index):
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

    def counter(self, tokens, index):
        while tokens[index].typ != 'ENDLINE':
            index += 1
        return index

    def NotPolonesa(self, tokens, index):
        pilha = []
        pilha.append('(')
        while (tokens[index].typ != 'ENDLINE'):

            if tokens[index].value == '(':
                pilha.append(tokens[index].value)
                index += 1
            elif tokens[index].value == ')':
                while pilha[len(pilha) - 1] != '(':
                    self.code.append(pilha.pop())
                pilha.pop()
                index += 1
            elif tokens[index].typ == 'ID':
                self.CRVL(index)
                index += 1
            elif tokens[index].typ == 'NUMBER':
                self.CRCTI(index)
                index += 1
            elif tokens[index].value == '+':
                pilha.append("SOMA \n")
                index += 1
            elif tokens[index].value == '-':
                pilha.append("SUBT \n")
                index += 1
            elif tokens[index].value == '*':
                if tokens[index + 1].typ == 'ID':
                    self.CRVL(index + 1)
                elif tokens[index + 1].typ == 'NUMBER':
                    self.CRCTI(index + 1)
                self.code.append("MULT \n")
                index += 2
            elif tokens[index].value == '/':
                if tokens[index + 1].typ == 'ID':
                    self.CRVL(index + 1)
                elif tokens[index + 1].typ == 'NUMBER':
                    self.CRCTI(index + 1)
                self.code.append("DIVI \n")
                index += 2
            elif tokens[index].typ == 'VIR':
                break
        while len(pilha) != 1:
            self.code.append(pilha.pop())


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

    with open('tokens_list.txt', 'w') as file:
        for el in toke:
            file.writelines(str(el) + "\n")


    texto = tradutor.translate(toke, 0, len(toke))
    print(texto)

    arq = open("traducao.txt", "w")
    arq.writelines(texto)
    arq.close()
