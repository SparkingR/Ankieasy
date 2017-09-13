#!/usr/bin/env python
import sys
import json
import importlib
import os

sys.path.append('anki')
from anki import Collection as aopen

def initAnkiModule(data, card_type):
    if "collection" not in data or "deck" not in data:
        return None
    deck = aopen(data['collection'])
    deckId = deck.decks.id(data['deck'])

    deck.decks.select(deckId)
    model = deck.models.byName(card_type.GetCardType(deck.models))
    model['did'] = deckId
    deck.models.save(model)
    deck.models.setCurrent(model)
    return deck

def handleProfile(data):
    print('words file:{}'.format(data['file']))
    print('deck file:{}'.format(data['deck']))
    print('collection file:{}'.format(data['collection']))
    print('media file :{}'.format(data['download_dir']))
    print('dict_source :{}'.format(data['dict_source']))
    print('card_type:{}'.format(data['card_type'] if 'card_type' in data else 'Basic'))

    if 'file' not in data:
        print("No input file, Exit")
        return
    input_file = "{}/{}".format(os.getcwd(), data['file'])

    card_type = data['card_type'] if 'card_type' is data else 'basic'

    dict_source = importlib.import_module('module.{}'.format(data['dict_source'].lower()))
    card_type = importlib.import_module('cardtype.{}'.format(card_type))
    deck = initAnkiModule(data,card_type)
    with open(input_file , encoding='utf-8') as word_list:
        for word in word_list:
            result = dict_source.LookUp(word, data)
            card_data = card_type.MakeCard(result)
            card = deck.newNote()
            for key in card_data:
                card[key] = card_data[key]
            try:
                deck.addNote(card)
            except(Exception, e):
                if hasattr(e, "data"):
                    sys.exit("ERROR: Cound not add {}:{}", e.data["field"], e.data['type'])
                else:
                    sys.exit(e)
    deck.save()
    deck.close()

def load_config(path):
    with open(path, encoding='utf-8') as data_file:
        return json.load(data_file)

if '__main__':
    if len(sys.argv) >= 2:
        config_path = sys.argv[1]
    else:
        config_path = 'config.json'
    data = load_config(config_path)
    for profile in data['profiles']:
        handleProfile(profile)
