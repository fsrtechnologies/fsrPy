#-------------------------------------------------------------------------------
# Name:        fsrDeck
# Purpose:     Card primitives
#
# Author:      Marc
#
# Created:     13/09/2015
# Copyright:   (c) Marc 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------
# coding: utf-8
import random

class Card(object):
    def __init__(self, cardSuit, cardValue):
        self.suit  = cardSuit
        self.points = self.value = cardValue
        self.name  = str(cardValue)
        if cardValue == 1 and cardSuit != 'J':
            self.name = u'A'
        elif cardValue == 11:
            self.name = u'J'
            self.points = 10
        elif cardValue == 12:
            self.name = u'Q'
            self.points = 10
        elif cardValue == 13:
            self.name = u'K'
            self.points = 10
        self.name = "{}{}".format(self.name, self.suit)
    def __str__(self):
        return self.name

class Hand(list):
    """
    Technically just a stack of cards - the Reserve is a Hand - but didn't want
    to use Stack; it feels too much like a reserved word.
    """
    def __init__(self, *args):
        list.__init__(self, *args)
    def __str__(self):
        tmpStr = ''
        for card in self.__iter__():
            tmpStr += " " + card.name
        return tmpStr

class Deck(object):
    Hands = []
    Reserve = Hand()
    upCard = None
    def __init__(self, numPacks=1, numJokers=0):
        for packs in range(numPacks):
            for suit in ('S', 'C', 'H', 'D'):
                for value in range(1,14):
                    self.Reserve.append(Card(suit, value))
            for joker in range(numJokers):
                self.Reserve.append(Card('J', joker))
    def __str__(self):
        outString = ""
        count = 0
        for card in self.Reserve:
            count += 1
            outString = outString + card.name + "  "
            if count % 13 == 0:
                outString = outString + "\n"
        outString = outString + "\n\n"
        return outString

    def shuffle(self, seedFix=None):
        random.seed(seedFix)
        random.shuffle(self.Reserve)

    def deal(self, numHands=2, cardsPer=6):
        assert (numHands*cardsPer) <= len(self.Reserve)
        for hand in range(numHands):
            self.Hands.append(Hand())
        for card in range(cardsPer):
            for hand in self.Hands:
                thisCard = self.Reserve.pop(0)
                hand.append(thisCard)
        return self.Hands

    def turn(self, sliceLevel=None):
        if sliceLevel == None:
            sliceLevel = random.randint(0,len(self.Reserve))
        self.upCard = self.Reserve.pop(sliceLevel)
        return self.upCard

def main():
    deck = Deck(1, 2)
    #deck.shuffle(10)
    deck.deal(3, 5)
    for hand in deck.Hands:
        print hand
    deck.turn(0)
    print deck.upCard
    print deck.Reserve

if __name__ == '__main__':
    main()


