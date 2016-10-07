#!/usr/bin/python
# -*- coding: utf-8-sig -*-

from flask import Flask, request, render_template, redirect
from random import random
app = Flask(__name__)


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


@app.route('/empty')
def empty():
    return render_template("empty.html", args=request.args.getlist('collection'))

app.run(debug=True)
