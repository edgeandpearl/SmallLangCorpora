#encoding=utf-8
__author__ = 'Basilis'
import json
import codecs
import lxml.etree
import re
import sys
import os

# два типа агрегатов: документ и коллекция

# collection = {x: {'type': 'string', 'value': ''} \
# for x in 'name language year authors place'.split()} \
#    + {'layers': {'group_name': ['layer_names']}}


def open_file(x):
    print("opening file {}...".format(x))
    f = codecs.open(x, 'r', 'utf-8-sig')
    text = f.read()
    f.close()
    return text


def prep(text):
    text = re.sub(u'\s{2,}', u'', text)
    """M`s change"""
#    text = re.sub(u'</word><word><words>', u'<border>', text)
#    text = re.sub(u'<word><words>(.+?)<border>', u'<phrase><words>\\1</phrase><phrase><words>', text)
#    text = re.sub(u'(.+?)<border>', u'\\1</phrase><phrase><words>', text)
#    text = re.sub(u'(.+?)</word></phrases>', u'\\1</phrase></phrases>', text)
    text = re.sub('<word>(\s*<words>\s*<word>)', '<phrase>\\1', text)
    text = re.sub('/></word>', '/></phrase>', text)
    text = text.replace(u'<?xml version="1.0" encoding="utf-8"?>', u'')
    root = lxml.etree.fromstring(text)
    return root


def add_attr(root):
    """input: <tag attrib=x>
       output: tag, {attrib: x}
       """
    if root.tag == 'item':
        head = root.get("type")
        root.attrib.pop("type")
        if head == "age.n":
            head = "age"
    else:
        head = root.tag
    attr = {x: root.attrib[x] for x in root.attrib if x != "guid"}
    # maybe we'll need guid later buut
    return head, attr


def assign_vals(root):
    """decides what's to be the head aka json key"""
    mp = {}
    if root.attrib:
        head, attr = add_attr(root)
        mp[head] = attr
    else:
        head = root.tag
        mp[head] = {}
    if root.text:
        mp[head]["value"] = root.text
    return mp


def join_dash_or_nil(arr):
    res = arr[0]
    for i in range(len(arr)-1):
        if (not res.endswith('-')) & (not arr[i+1].startswith('-')):
            res = '-'.join([res, arr[i+1]])
        else:
            res = ''.join([res, arr[i+1]])
    return res


def parse_sentences(paragraphs):
    """gets text, returns array of sentences parsed and joined with words in them"""
    sents = paragraphs.xpath('.//phrase')
    layers = [layer.get('type') for layer in sents[0].xpath('.//morph')[0].getchildren()]
    sentences = []
    for sent in sents:
        sentence = {}
        words = sent.xpath('.//word')
        # for words
        words_obj = []
        for word in words:
            # now adding words
            word_agr = {}
            for i, lay in enumerate(['words', 'pos']):
                try:
                    sentence[lay] = ' '.join([sentence.get(lay, ''), word.getchildren()[i].text]).strip()
                    word_agr[lay] = word.getchildren()[i].text
                except:
                    sentence[lay] = ' '.join([sentence.get(lay, ''), word.getchildren()[0].text])
            for layer in layers:
                try:
                    morphs = join_dash_or_nil([item.text for item \
                            in word.xpath('.//morph/item[@type="{}"]'.format(layer))])
                    word_agr[layer] = morphs
                except:
                    morphs = word.getchildren()[0].text
            sentence[layer] = ' '.join([sentence.get(layer, ''), morphs]).strip()
            # print(word_agr)
            word_agr = join_layers(word_agr, 'word')
            # print(word_agr)
            words_obj.append(word_agr)
        sentence = join_layers(sentence, 'phrase')
        sentence['phrase']['translations'] = [item.text for item in sent.xpath('./item')] # [@type="gls"]
        sentence['phrase']['words_objs'] = words_obj
        # print(sentence)
        sentences.append(sentence)
    return sentences

def join_layers(dic, root):
    # we have words, gls, pos, translations, morphemes; words dnt have translations
    output = {}
    for i in ['words', 'pos', 'gls']:
        try:
            output[i] = dic[i]
            del dic[i]
        except:
            pass
    if 'gls' not in dic:
        gls = []
        for lay in dic:
            if lay.startswith('g'):
                gls.append(dic[lay])
                del dic[lay]
        if gls:
            output['gls'] = gls
    if 'pos' not in dic:
        if 'ps' in dic:
            output['pos'] = dic['ps']
            del dic['ps']
    # all thats left is morphemes
    if len(dic)>0:
        output['morphemes'] = [dic[i] for i in dic]
    output = {root: output}
    return output

# also start adding new levels
# faskin lists!!
# lists: morphemes, words, phrases, languages
# let's move to naming
# GLS!!!
# OK look up in the corp what else can be []
# or write a func that turns {} into [] if met
# ('d be much easier)
# 1. define head
# 2. collect attributes (both in assign_vals & add_attr)
# 3. collect children (in parse)
# 4. merge (in merger & findmore)


# if root.tag == "interlinear-text":


def collect_meta(doc):
    chars = doc.xpath('./item')
    kids = {}
    for ch in chars:
        mm = assign_vals(ch)
        kids.update(mm)
    mp = {"meta": kids}
    return mp


def collect_content(doc):
    cont = doc.xpath('.//phrases')
    # mp = {'phrases': parse_sentences(cont[0])}
    mp = parse_sentences(cont[0])
    # mp = parse(cont[0])
    return mp


def main(name):
    try:
        if not os.path.exists("./src"):
            os.mkdir("./src")
        fil = prep(open_file(name))
        docs = fil.xpath('//interlinear-text')
        print(len(docs))
        for doc in docs:
            filename = doc.xpath('//item[@type="title"]')[0].text
            try:
                sys.stdout.write("Collecting %s\n" % filename)
                meta = collect_meta(doc)
                content = collect_content(doc)
                document = {'document': meta}
                # content.update(meta)
                # content = {"document": content} # warning: content is a list now
                # with codecs.open(os.path.join("src", filename + '.json'), 'w', 'utf-8-sig') as outfile:
                #     json.dump(content, outfile)
                yield content, document
            except:
                print("failed collecting content with {}".format(filename))
    except:
        print("failed opening with {}".format(name))


def copy_main(name):
    fil = prep(open_file(name))
    docs = fil.xpath('//interlinear-text')
    print(len(docs))
    for doc in docs:
        filename = doc.xpath('.//item[@type="title"]')[0].text
        sys.stdout.write("Collecting %s\n" % filename)
        meta = collect_meta(doc)
        # meta.update(collect_content(doc))
        # meta.update(collect_langs(doc))
        # result = {"document": meta}
        # with codecs.open(filename + '.json', 'w', 'utf-8-sig') as outfile:
        #     json.dump(result, outfile)
        # content = collect_content(doc)
        content = collect_content(doc)
        content.update(meta)
        content = {"document": content}
        with codecs.open(os.path.join(filename + '.json'), 'w', 'utf-8-sig') as outfile:
            json.dump(content, outfile)
        # with codecs.open(os.path.join(filename + '_meta.json'), 'w', 'utf-8-sig') as outfile:
        #     json.dump(meta, outfile)
        yield content



if __name__ == "__main__":
    """кусок для открытия"""
    # with open('Автобиографийа.json') as outfile:
    #     try:
    #         stri = json.load(outfile)
    #     except:
    #         outfile.seek(0)
    #         stri = json.loads(outfile.read()[3:])
    # print(stri["document"]["meta"]["title"]["value"])
    """кусок для обкачки"""
    # main("MokshaTmp.xml")
    for i in main("MokshaTmp.xml"):
        print('ok')
