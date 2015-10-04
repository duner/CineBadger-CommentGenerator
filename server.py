from flask import Flask, jsonify, render_template
import requests
import random
import datetime
import csv
import emoji

app = Flask(__name__)



@app.route('/movie/<movie_id>')
def movie_page(movie_id, methods=['GET']):
    context = get_data(movie_id)
    return render_template('results.html', **context)

@app.route('/query/<movie_id>')
def movie_endpoint(movie_id, methods=['GET']):
    data = get_data(movie_id)
    movie = Movie(data)
    response = {
        'title': movie.title,
        'messages': movie.get_comments()
    }
    return jsonify(response)


def get_data(movie_id):
    movie = {}

    rotten_key = 'b58afw2v2wk3ynvebzqugvwr'
    info_url = 'http://api.rottentomatoes.com/api/public/v1.0/movies/{}.json?apikey={}'.format(movie_id, rotten_key)
    review_url = 'http://api.rottentomatoes.com/api/public/v1.0/movies/{}/reviews.json?apikey={}'.format(movie_id, rotten_key)

    movie['info'] = requests.get(info_url).json()
    movie['reviews'] = requests.get(review_url).json()['reviews']
    return movie


class Movie(object):
    def __init__(self, data):
        self.data = data

    def get_comments(self):
        with open('messages.csv', 'r') as f:
            messages = {}
            reader = csv.DictReader(f)
            data_list = list(reader)
            for data in data_list:
                review = self.review
                movie_data = {
                    'title': self.title,
                    'director': self.director,
                    'runtime': self.runtime,
                    'releasedate': self.releasedate,
                    'actor': self.actors[0],
                    'actor2': self.actors[1],
                    'review_q': review['quote'],
                    'review_pub': review['pub'],
                    'review_critic': review['critic'],
                    'rtblurb': self.rtblurb
                }

                for tag in data['Tags'].split(','):
                    tag = tag.strip()
                    if tag not in messages.keys():
                        messages[tag] = []
                    message = data['Message'].format(**movie_data)
                    message = emoji.emojize(message, use_aliases=True)
                    messages[tag].append(message)
        return messages

    @property
    def title(self): return self.data['info']['title']

    @property
    def actors(self):
        return [d['name'] for d in self.data['info']['abridged_cast']]

    @property
    def director(self):
        return [d['name'] for d in self.data['info']['abridged_directors']][0]

    @property
    def runtime(self): return str(self.data['info']['runtime']) + ' minutes'

    @property
    def rtblurb(self):
        blurb = self.data['info']['critics_consensus']
        if not blurb:
            rand = random.random()
            if rand > 0.5:
                blurb = "{} has been called a film with a beginning, middle, AND end.".format(self.title)
            else:
                blurb = "{} has been called a film with a beginning, middle, AND end.".format(self.title)
        return blurb

    @property
    def releasedate(self):
        arr = self.data['info']['release_dates']['theater'].split('-')
        date = datetime.date(int(arr[0]), int(arr[1]), int(arr[2]))
        return date.strftime("%B %-d, %Y")

    @property
    def review(self):
        review = random.choice(self.data['reviews'])
        return {
            'critic': review['critic'],
            'pub': '"' + review['publication'] + '"',
            'quote': '"' + review['quote'] + '"'
        }


if __name__ == "__main__":
    app.run(debug=True, port=5000)
