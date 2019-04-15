#-------------------------------------------------------------------------------
# Name:        fsrCounting
# Purpose:     Counting cribbage hands
#
# Author:      Marc
#
# Created:     13/09/2015
# Copyright:   (c) Marc 2015
# Licence:     <your licence>
#-------------------------------------------------------------------------------
# coding: utf-8
from fsrDeck import Deck, Hand

def main():
    deck = Deck(1, 2)
    deck.shuffle(10)
    deck.deal(3, 5)
    for hand in deck.Hands:
        print hand
    deck.turn(0)
    print deck.upCard
    print deck.Reserve

if __name__ == '__main__':
    main()
