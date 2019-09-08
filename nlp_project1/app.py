#!/usr/bin/python
#coding:utf-8
from flask import Flask, jsonify, request
from flask import render_template
from flask import abort, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Length
from wtforms.widgets import TextArea
from nlp import execute


app = Flask(__name__)
Bootstrap(app)
app.secret_key = 'dev'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/nlp_test1'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db = SQLAlchemy(app)

class TraindataSource(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=True)
    content = db.Column(db.Text(16777216))
    results = db.relationship('TrainResult', backref='traindata_source', lazy=True)

    def __init__(self, content):
        self.content = content

    def __repr__(self):
        return '<Content %s>' % self.content

class TrainResult(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=True)
    subject = db.Column(db.String(255))
    verb = db.Column(db.String(255))
    sentence = db.Column(db.Text(65536))
    traindata_source_id= db.Column(db.Integer, db.ForeignKey('traindata_source.id'),
        nullable=False)

    def __init__(self, subject,verb,sentence,traindata_source_id):
        self.subject = subject
        self.verb = verb
        self.sentence = sentence
        self.traindata_source_id = traindata_source_id

    def __repr__(self):
        return '<Content %s>' % self.sentence


class HelloForm(FlaskForm):
    content = StringField('', widget=TextArea(), validators=[DataRequired(), Length(1, 20)])
    # password = PasswordField('Password', validators=[DataRequired(), Length(8, 150)])
    # remember = BooleanField('Remember me')
    submit = SubmitField()

@app.route('/')
def hello_world():
    page = request.args.get('page', 1, type=int)
    form = HelloForm()

    pagination = TraindataSource.query.order_by(TraindataSource.id.desc()).paginate(page, per_page=2)
    sources = pagination.items

    return render_template('list.html', form=form,
                pagination=pagination, sources=sources)

@app.route('/task', methods=['POST'])
def add_task():
    content = request.form['content']
    if not content:
        return 'Error'
    print(content)
    
    source = TraindataSource(content)
    db.session.add(source)
    db.session.flush()
    results = execute(content)
    for result in results:
        res = TrainResult(result['subject'], result['verb'], result['sentence'], source.id)
        db.session.add(res)
    db.session.commit()

    return redirect('/')

if __name__=='__main__':
    # app.debug = True
    app.run(host='0.0.0.0',port=5001)
