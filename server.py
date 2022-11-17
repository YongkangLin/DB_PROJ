import os
import re
import sys
import random
import string
import logging
from datetime import datetime
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
auth = HTTPBasicAuth()
app = Flask(__name__, template_folder=tmpl_dir)
DATABASEURI = "postgresql://aea2185:1936@34.75.94.195/proj1part2"
engine = create_engine(DATABASEURI)
logging.basicConfig(level=logging.DEBUG)

users = {
    "Yong": generate_password_hash("pog"),
    "Antonio": generate_password_hash("mid")
}

@auth.verify_password
def verify_password(username, password):
  if username in users and \
      check_password_hash(users.get(username), password):
    return username

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

@app.route('/admin')
@auth.login_required
def admin():
  data = []
  airport = []
  airplane = []
  pilot = []
  cursor = g.conn.execute("SELECT code FROM airport;")
  cursor2 = g.conn.execute("SELECT pilotid FROM pilot;")
  cursor3 = g.conn.execute("SELECT numid FROM airplane;")
  for i in cursor:
    i = i._asdict()
    airport.append(i['code'])
  for i in cursor2:
    i = i._asdict()
    pilot.append(i['pilotid'])
  for i in cursor3:
    i = i._asdict()
    airplane.append(i['numid'])
  data.append(airport)
  data.append(airplane)
  data.append(pilot)
  data.append(auth.current_user())
  return render_template("admin.html",data=data)

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
      price = round(random.uniform(50,500),2)

      for i in range(random.randint(3,10)):
        seat = str(random.randint(1,30)) + random.choice(['A','B','C','D','E'])
        seats.append(seat)
      result['takeoff'] = result['takeoff'].strftime('%Y-%m-%d %H:%M:%S')
      result['landing'] = result['landing'].strftime('%Y-%m-%d %H:%M:%S')
      result['price'] = price
      result['seats'] = seats
      airplane = g.conn.execute("SELECT capacity FROM airplane WHERE numid = '{}';".format(result['numid']))
      for capacity in airplane:
        result['capacity'] = capacity['capacity']
      flights.append(result)
    cursor.close()
    if len(flights) > 0:
      return render_template("booking.html", data=[form,flights])
    else:
      return render_template("booking.html", data=[])
  return render_template("booking.html", data=[])

@app.route('/modairport',methods=['POST'])
def modairport():
  code = request.form['code']
  city = request.form['city']
  country = request.form['country']
  if request.form['submit'] == 'add':
    g.conn.execute("INSERT INTO airport VALUES('{}','{}','{}');".format(code,city,country))
  if request.form['submit'] == 'delete':
    g.conn.execute("DELETE FROM airport WHERE code ILIKE '{}';".format(code))
  return redirect('/admin')

@app.route('/modflight',methods=['POST'])
def modflight():
  flightnum = request.form['flightnum']
  depart = request.form['depart']
  arrival = request.form['arrival']
  takeoff = request.form['takeoff'].replace('T',' ') + ':00'
  landing = request.form['landing'].replace('T',' ') + ':00'
  app.logger.debug(takeoff)
  plane = request.form['numid']
  pilot = request.form['pilot']
  if request.form['submit'] == 'add':
    q = "INSERT INTO flight VALUES('{}','{}','{}',".format(flightnum,takeoff,landing)
    q += "'0','{}','{}','{}');".format(depart,arrival,plane)
    g.conn.execute(q)
    g.conn.execute("INSERT INTO departs_from VALUES('{}','{}','{}');".format(flightnum,takeoff,depart))
    g.conn.execute("INSERT INTO lands_in VALUES('{}','{}','{}');".format(flightnum,takeoff,arrival))
    g.conn.execute("INSERT INTO flown_by VALUES('{}','{}','{}');".format(pilot,flightnum,takeoff))
    g.conn.execute("INSERT INTO assigned_to VALUES('{}','{}','{}');".format(plane,flightnum,takeoff))
  if request.form['submit'] == 'delete':
    g.conn.execute("DELETE FROM flight WHERE flightnum = '{}' and takeoff = '{}';".format(flightnum,takeoff))
    g.conn.execute("DELETE FROM lands_in WHERE flightnum = '{}' and takeoff = '{}';".format(flightnum,takeoff))
    g.conn.execute("DELETE FROM departs_from WHERE flightnum = '{}' and takeoff = '{}';".format(flightnum,takeoff))
    g.conn.execute("DELETE FROM assigned_to WHERE flightnum = '{}' and takeoff = '{}';".format(flightnum,takeoff))
  return redirect('/admin')

@app.route('/modpilot',methods=['POST'])
def modpilot():
  pilotid = request.form['id']
  name = request.form['name']
  fhours = request.form['hours']
  rank = request.form['rank']
  if request.form['submit'] == 'add':
    g.conn.execute("INSERT INTO pilot VALUES('{}','{}','{}','{}');".format(pilotid,name,fhours,rank))
  if request.form['submit'] == 'delete':
    g.conn.execute("DELETE FROM pilot WHERE pilotid ILIKE '{}';".format(pilotid))
  return redirect('/admin')

@app.route('/modplane',methods=['POST'])
def modplane():
  numid = request.form['numid']
  manufacturer = request.form['manufacturer']
  model = request.form['model']
  fleet = request.form['fleet']
  capacity = request.form['capacity']
  if request.form['submit'] == 'add':
    query = ("INSERT INTO airplane VALUES(" + 
    "'{}','{}','{}','{}','{}');".format(numid,manufacturer,model,fleet,capacity))
    g.conn.execute(query)
  if request.form['submit'] == 'delete':
    g.conn.execute("DELETE FROM airplane WHERE numid ILIKE '{}';".format(numid))
  return redirect('/admin')

@app.route('/cancel',methods=['POST'])
def cancel():
  confirm = request.json[0][0]
  g.conn.execute("DELETE FROM booked_by WHERE confirm ILIKE '{}';".format(confirm))
  g.conn.execute("DELETE FROM booked_on WHERE confirm ILIKE '{}';".format(confirm))
  g.conn.execute("DELETE FROM booking WHERE confirm ILIKE '{}';".format(confirm))
  return redirect('/manage')

@app.route(
  '/book', methods=['POST'])
def book():
  content = request.json
  pid = content[0][0]
  name = content[0][1]
  bday = content[0][2]
  ID = content[0][3]
  confirm = content[0][7] 
  seat = content[0][8]
  takeoff = content[1]['takeoff']
  price = content[1]['price']
  flightnum = content[1]['flightnum']
  booktime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  g.conn.execute("INSERT INTO passenger VALUES('{}','{}','{}','{}');".format(pid,name,bday,ID))
  g.conn.execute("INSERT INTO booking VALUES('{}','{}','{}','{}','{}','{}','{}');".format
  (confirm,price,seat,flightnum,takeoff,pid,booktime))
  g.conn.execute("INSERT INTO booked_by VALUES('{}','{}');".format(pid,confirm))
  g.conn.execute("INSERT INTO booked_on VALUES('{}','{}','{}');".format(confirm,flightnum,takeoff))
  cursor = g.conn.execute("SELECT * FROM booked_on WHERE flightnum = '{}' and takeoff = '{}';".format(flightnum,takeoff))  
  g.conn.execute("UPDATE flight SET passengers = '{}' WHERE flightnum = '{}' and takeoff = '{}';".format(len(list(cursor)),flightnum,takeoff))
  return redirect('/booking')


@app.route('/manage', methods=['GET','POST'])
def manage():
  if request.method == 'POST':
    flights = []
    confirm = request.form['confirm'] 
    ID = request.form['id']
    query = "select * from (select flightnum, takeoff from (select "
    query+= "confirm from booked_by as b,(select pid from passenger where idnum = '{}') as a where".format(ID)
    query += " b.pid = a.pid) as c, booked_on as d where c.confirm = d.confirm and d.confirm = "
    query+= "'{}') as e, flight as f where e.flightnum = f.flightnum and e.takeoff = f.takeoff;".format(confirm)
    cursor = g.conn.execute(query)
    for result in cursor:
      result = result._asdict()
      airplane = g.conn.execute("SELECT capacity FROM airplane WHERE numid = '{}';".format(result['numid']))
      for capacity in airplane:
        result['capacity'] = capacity['capacity']
      flights.append(result)
    cursor.close()
    if len(flights) > 0:
      return render_template("manage.html", data=[flights,confirm])
    else:
      return render_template("manage.html", data=[])
  return render_template("manage.html", data=[])

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
