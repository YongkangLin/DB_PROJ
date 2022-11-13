import os
import random
import string
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
DATABASEURI = "postgresql://aea2185:1936@34.75.94.195/proj1part2"
engine = create_engine(DATABASEURI)

@app.before_request
def before_request():
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  try:
    g.conn.close()
  except Exception as e:
    pass

@app.route('/')
def index():
  return render_template("index.html")

@app.context_processor
def seat():
  seats = []
  for i in range(random.randint(3,10)):
    seat = str(random.randint(1,30)) + random.choice(string.ascii_uppercase)
    seats.append(seat)
  return dict(seats=seats)

@app.route('/booking', methods=['GET','POST'])
def booking():
  if request.method == 'POST':
    flights = []
    depart = request.form['depart'] 
    arrival = request.form['arrival']
    takeoff = request.form['takeoff']
    query = ("SELECT * FROM flight WHERE departcode ILIKE '{}' and ".format(depart) + 
    "arrivalcode ILIKE '{}' and DATE(takeoff) = '{}';".format(arrival,takeoff))
    cursor = g.conn.execute(query)
    for result in cursor:
      flights.append(result)
    cursor.close()
    if len(flights) > 0:
      return render_template("booking.html", data=[flights])
    else:
      return render_template("booking.html", data=[])
  return render_template("booking.html", data=[])

@app.route('/book',methods=['POST'])
def book():
  pid = random.randint(0, 999999)
  name = request.form['name']
  bday = request.form['bday']
  id = request.form['ID']

@app.route('/lookup', methods=['GET','POST'])
def lookup():
  if request.method == 'POST':
    flights = []
    confirm = request.form['confirm'] 
    query = ("SELECT * FROM flight as f, (SELECT flightnum FROM booked_on " + 
    "WHERE confirm = '{}') as s WHERE f.flightnum = s.flightnum;".format(confirm))
    cursor = g.conn.execute(query)
    for result in cursor:
      flights.append(result)  # can also be accessed using result[0]
    cursor.close()
    if len(flights) > 0:
      return render_template("lookup.html", data=[flights])
    else:
      return render_template("lookup.html", data=[])
  return render_template("lookup.html", data=[])

if __name__ == "__main__":
  import click
  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)
  run()