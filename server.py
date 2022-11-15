import os
import sys
import random
import string
import logging
import datetime
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
DATABASEURI = "postgresql://aea2185:1936@34.75.94.195/proj1part2"
engine = create_engine(DATABASEURI)
logging.basicConfig(level=logging.DEBUG)

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
  seats = set()
  for i in range(random.randint(3,10)):
    seat = str(random.randint(1,30)) + random.choice(['A','B','C','D','E'])
    seats.add(seat)
  return dict(seats=seats)

@app.route('/booking', methods=['GET','POST'])
def booking():
  if request.method == 'POST':
    form = []
    flights = []
    pid = random.randint(0, 999999)
    confirm = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
    name = request.form['name']
    bday = request.form['bday']
    id = request.form['ID']
    depart = request.form['depart']
    arrival = request.form['arrival']
    takeoff = request.form['takeoff']
    form.append(pid)
    form.append(name)
    form.append(bday)
    form.append(id)
    form.append(depart)
    form.append(arrival)
    form.append(takeoff)
    form.append(confirm)
    query = ("SELECT * FROM flight WHERE departcode ILIKE '{}' and ".format(depart) + 
    "arrivalcode ILIKE '{}' and DATE(takeoff) = '{}';".format(arrival,takeoff))
    cursor = g.conn.execute(query)
    for result in cursor:
      seats = []
      result = result._asdict()
      price = "$" + str(round(random.uniform(50,500),2))

      for i in range(random.randint(3,10)):
        seat = str(random.randint(1,30)) + random.choice(['A','B','C','D','E'])
        seats.append(seat)
      result['takeoff'] = result['takeoff'].strftime('%Y-%m-%d %H:%M:%S')
      result['landing'] = result['landing'].strftime('%Y-%m-%d %H:%M:%S')
      result['price'] = price
      result['seats'] = seats
      app.logger.debug(result)
      flights.append(result)
    cursor.close()
    if len(flights) > 0:
      return render_template("booking.html", data=[form,flights])
    else:
      return render_template("booking.html", data=[])
  return render_template("booking.html", data=[])

@app.route('/success', methods=['GET','POST'])
def success():
  return render_template("success.html")

@app.route('/book', methods=['POST'])
def book():
  content = request.json
  app.logger.debug(content)
  pid = content[0][0]
  name = content[0][1]
  bday = content[0][2]
  ID = content[0][3]
  query = ("INSERT INTO passenger VALUES('{}','{}','{}','{}');".format(pid,name,bday,ID))
  cursor = g.conn.execute(query)
  app.logger.debug(request.json)
  return redirect('/booking')


@app.route('/lookup', methods=['GET','POST'])
def lookup():
  if request.method == 'POST':
    flights = []
    confirm = request.form['confirm'] 
    query = ("SELECT * FROM flight as f, (SELECT flightnum FROM booked_on " + 
    "WHERE confirm = '{}') as s WHERE f.flightnum = s.flightnum;".format(confirm))
    cursor = g.conn.execute(query)
    for result in cursor:
      flights.append(result)
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
    app.run(host=HOST, port=PORT, debug=True, threaded=threaded)
  run()
