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
        result = ''
        dict_morph = {}
        dict_text = {}
        dict_gloss = {}
        dict_transl = {}
        dict_pos = {}
        q = {"query": {"bool": {"should": []}}}

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

        q["query"]["bool"]["should"] += [dict_morph] + [dict_pos] + [dict_transl] + [dict_gloss] + [dict_text]
        res = es.search(index="smallangs", body=q)
        hit = res['hits']['hits'][0]
        result = u'Текст: ' + unicode(hit['_source']['words']) + u'<br>Перевод: '
        for i in hit['_source']['translations']:
            if i != None:
                result += i + '<br>'
        result += u'Морфемы: '
        for i in hit['_source']['morphemes']:
            result += i + '<br>'
        result += u'Части речи: ' + unicode(hit['_source']['pos']) \
                 + u'<br>Глоссы: ' + unicode(hit['_source']['gls'])

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
