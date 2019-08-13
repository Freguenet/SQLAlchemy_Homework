import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker

from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

print(Base.classes.keys())
# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# set up flask
app = Flask(__name__)

# set up routes

@app.route("/")
def welcome():
    return (
        f"Available routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<end><br/>"
        f"For the last two routes, enter a start date and range date, respectivily, in the 'yyyy-mm-dd' format"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """List of precipitation"""
    
    maximum_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    max_date = maximum_date[0]

    ### Calculate the date 1 year ago from the last data point in the database
    previous_year = dt.datetime.strptime(max_date, "%Y-%m-%d") - dt.timedelta(days=366)

    # Perform a query to retrieve the data and precipitation scores
    query_precipitation = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= previous_year).all()

    # Convert list of tuples into dictionary
    dict_prcp = dict(query_precipitation)

    # jsonify the dictionary
    return jsonify(dict_prcp)

@app.route("/api/v1.0/stations")
def stations():
    
    """JSON list of stations from the dataset"""

    # Query the stations
    active_stations = session.query(Measurement.station).group_by(Measurement.station).all()
    list_stations = list(np.ravel(active_stations))

    # Jsonify the list
    return jsonify(list_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    """JSON list of temperature observations for the last 366 days"""

    # Query to get the precipitation data 
    maximum_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    max_date = maximum_date[0]

    ### Calculate the date 1 year ago from the last data point in the database
    one_year_ago = dt.datetime.strptime(max_date, "%Y-%m-%d") - dt.timedelta(days=366)
    query_tobs = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= one_year_ago).all()

    # List
    list_tobs = list (query_tobs)

    #Jsonify the list
    return jsonify(list_tobs)


@app.route("/api/v1.0/<start>")
def start(start = None):

    """JSON list of tmin, tmax, tavg for the dates greater than/equal to date entered"""
    
    # Query start date
    query_startdate = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).group_by(Measurement.date).all()
    
    # List
    list_startdate = list(query_startdate)

    # Jsonify the list
    return jsonify(list_startdate)

@app.route("/api/v1.0/<start>/<end>")
def end(start = None, end = None):
   
    """JSON list of tmin, tmax, tavg """

    if end == None: 
        end1 = session.query(func.max(Measurement.date)).first()[0]
    # Query
    query_rangedates = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end1).all()

    # List
    list_rangedates = list(query_rangedates)
    
    # Jsonify the list
    return jsonify(list_rangedates)

if __name__ == '__main__':
    app.run(debug=True)