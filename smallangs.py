#!/usr/bin/python
# -*- coding: utf-8-sig -*-

from flask import Flask, render_template, Response, redirect, url_for, request, session, abort
from random import random
from elasticsearch import Elasticsearch

es = Elasticsearch()

app = Flask(__name__)
app.secret_key = 'R2TujPXzu3KJnSaeZ'

collections = {"khakas": (u"Хакасская коллекция", ""), "ket": (u"Кетская коллекция 1", u"Кетская коллекция 2", ""),
               "chukchi": (u"Чукотская коллекция", ""), "itelmen": (u"Ительменская коллекция", "")}
lang_names = {"khakas": u"Хакасский", "ket": u"Кетский", "chukchi": u"Чукотский", "itelmen": u"Ительменский"}
lang_info = {"khakas": u"язык хакасов. Распространён, главным образом, на территории Хакасии и частично в Шарыповском районе Красноярского края и Туве. Число говорящих на хакасском языке в России — 42 604 человека (2010). Относится к хакасско-алтайской группе восточной ветви тюркских языков.", 
             "ket": u"изолированный язык, единственный живой представитель енисейской семьи языков. На нём говорят кеты в районе бассейна реки Енисей. ",
             "chukchi": u"язык чукчей, один из языков чукотско-камчатской семьи. Чукотский язык распространён на территории Чукотского автономного округа, в северо-восточной части Корякского округа, а также в Нижне-Колымском районе республики Саха (Якутия).",
             "itelmen": u"язык ительменов, один из языков чукотско-камчатской группы."}


@app.route('/')
def index():
    if not request.args:
        return render_template('main.html')
    else:
        return render_template('collections.html', langs=request.args.getlist('lang'),
                               lang_names=lang_names, collections=collections)


@app.route('/language/<lang>')
def language_meta(lang):
    if lang.lower() in lang_names:
        with open("sampletext.txt") as f:
            text = f.read()
        w_size = int(random() * 1000)
        c_size = len(collections[lang])-1
        return render_template('lang_info.html', lang=lang, lang_name=lang_names[lang], text=text,
                               c_size=c_size, w_size=w_size)
    else:
        return render_template('empty.html', args=request.args.getlist('collection'))


@app.route('/query')
def query():
    if request.args:
        return render_template("query.html", collections=request.args.getlist('collection'))
    else:
        return redirect("/")


@app.route('/result')
def result():
    if request.args:
        morph = request.args['morph']
        text = request.args['text']
        gloss = request.args['gloss']
        transl = request.args['transl']
        pos = request.args['pos']
        selected_show = request.args.getlist('show')

        result = ''
        dict_morph = {}
        dict_text = {}
        dict_gloss = {}
        dict_transl = {}
        dict_pos = {}

        '''
        q = {"from": 0, "size": 500, "query": {"bool": {"must": []}}}

        if morph:
            dict_morph = {"match": {}}
            dict_morph["match"]["morphemes"] = morph

        if pos:
            dict_pos = {"match": {}}
            dict_pos["match"]["pos"] = pos

        if text:
            dict_text = {"match": {}}
            dict_text["match"]["words"] = text

        if gloss:
            dict_gloss = {"match": {}}
            dict_gloss["match"]["gls"] = gloss

        if transl:
            dict_transl = {"match": {}}
            dict_transl["match"]["translations"] = transl

        q["query"]["bool"]["must"] += [dict_morph] + [dict_pos] + [dict_transl] + [dict_gloss] + [dict_text]
        res = es.search(index="smallangs", body=q)
        for hit in res['hits']['hits']:
            #if hit['_score'] >= 1.0:
            if 'txt' in selected_show:
                result += u'Текст: ' + unicode(hit['_source']['words']) + '<br>'
            if 'trn' in selected_show:
                result += u'Перевод: '
                for i in hit['_source']['translations']:
                    if i != None:
                        result += i + '<br>'
            if 'mph' in selected_show:
                result += u'Морфемы: '
                for i in hit['_source']['morphemes']:
                    result += i + '<br>'
            if 'pos' in selected_show:
                result += u'Части речи: ' + unicode(hit['_source']['pos']) + '<br>'
            if 'gls' in selected_show:
                result += u'Глоссы: ' + unicode(hit['_source']['gls'])
            # result += str(hit['_score']) + '<hr>'
            result += '<hr>'
        '''

        #txt, gls, pos, morph
        q2 = {"from": 0, "size": 500, "query": {"nested": {"path": "phrase.words_objs", "query": {"bool": {"must": []}}}}}

        if gloss:
            dict_gloss = {"match": {}}
            dict_gloss["match"]["phrase.words_objs.word.gls"] = gloss

        if morph:
            dict_morph = {"match": {}}
            dict_morph["match"]["phrase.words_objs.word.morphemes"] = morph

        if pos:
            dict_pos = {"match": {}}
            dict_pos["match"]["phrase.words_objs.word.pos"] = pos

        if text:
            dict_text = {"match": {}}
            dict_text["match"]["phrase.words_objs.word.words"] = text

        q2["query"]["nested"]["query"]["bool"]["must"] += [dict_text] + [dict_gloss] + [dict_pos] + [dict_morph]
        res = es.search(index="smallangs", body=q2)
        for hit in res['hits']['hits']:
            # if hit['_score'] >= 1.0:
            if 'txt' in selected_show:
                result += u'Текст: ' + unicode(hit['_source']['phrase']['words']) + '<br>'
            if 'trn' in selected_show:
                result += u'Перевод: '
                for i in hit['_source']['phrase']['translations']:
                    if i != None:
                        result += i + '<br>'
            if 'mph' in selected_show:
                result += u'Морфемы: '
                for i in hit['_source']['phrase']['morphemes']:
                    result += i + '<br>'
            if 'pos' in selected_show:
                result += u'Части речи: ' + unicode(hit['_source']['phrase']['pos']) + '<br>'
            if 'gls' in selected_show:
                result += u'Глоссы: ' + unicode(hit['_source']['phrase']['gls'])
            # result += str(hit['_score']) + '<hr>'
            result += '<hr>'

        return render_template("result.html", text=request.args.getlist('text'), transl=request.args.getlist('translation'),
                               gloss=request.args.getlist('gloss'), morph=request.args.getlist('morph'), pos=request.args.getlist('pos'),
                               full_match=request.args.getlist('full_match'), case_sensitive=request.args.getlist('case_sensitive'),
                               args=request.args, result=result)
    else:
        return redirect("/")


@app.route('/empty')
def empty():
    return render_template("empty.html", args=request.args.getlist('collection'))


@app.route('/help')
def help():
    return render_template("help.html")


@app.route('/about')
def about():
    return render_template("about.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session['username'] = request.form['username']
        return redirect('/')
    return render_template("login.html")


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')


app.run(debug=True)
