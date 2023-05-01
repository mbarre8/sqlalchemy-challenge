# Import the dependencies.

import numpy as np
import pandas as pd
import datetime as dt
from datetime import timedelta

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model

Base = automap_base()

# reflect the tables

Base.prepare(engine, reflect=True)

# Save references to each table

Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB

session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################

#start homepage
@app.route("/")
def welcome():
   # List of available API routes
    return (
        f"<h1>Welcome to the Climate App </h1>"
        f"<h2>Available Routes:</h2>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end")

@app.route("/api/v1.0/precipitation")
def precipitation():

    #Retrieving 12 months of data from most recent date in data
    one_year_past= dt.date(2017, 8, 23) - timedelta(days=365)
    
    #Using the past 12 months of data to get date and precipaption values
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= one_year_past).all()

    #Place results in dictionary with date as a key and precipitation as value
    precipitation = {date: prcp for date, prcp in results}

    session.close()

    #display the dictionary results as a json structure on api page
    return jsonify(precipitation)


@app.route("/api/v1.0/stations")
def stations():

    #Query all stations
    all_stations = session.query(Station.station).all() 

    # Convert query reults from list of tuples into normal list
    stations = list(np.ravel(all_stations))

    session.close()

    #display the dictionary results as a json structure on api page
    return jsonify(stations)

@app.route("/api/v1.0/tobs")
def tobs():

    #Retrieving 12 months of data from most recent date in data
    one_year_past= dt.date(2017, 8, 23) - timedelta(days=365)

    #Query session, pulling previous year temperature observations for the most active station 
    most_active_station = session.query(Measurement.tobs).filter(Measurement.date >= one_year_past).filter(Measurement.station== 'USC00519281').all()
    
    # Convert query reults from list of tuples into normal list
    tobs = list(np.ravel(most_active_station))

    session.close()

    #display the dictionary results as a json structure on api page
    return jsonify(tobs)

@app.route("/api/v1.0/<start>")
def start(start):

    #Created query session looking for min, max and average temperature observations for specific start date to most recent date
    results1 = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start).all()
    
    # Convert query reults from list of tuples into normal list
    data= list(np.ravel(results1))

    session.close()

    #display the dictionary results as a json structure on api page
    return jsonify(data)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start = None, end =None):

    #Created query session looking for min, max and average temperature observations for specific start and end date 
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    
    # Convert query reults from list of tuples into normal list
    data1 = list(np.ravel(results))

    session.close()

    #display the dictionary results as a json structure on api page
    return jsonify(data1)

## The /api/v1.0/<start> and /api/v1.0/<start>/<end> both return 3 null values since no dates are specified 
## When you enter actually date, for start/end example "/api/v1.0/2016-08-23/2016-08-26" the return results in the api page is [74.0, 84.0, 78.88888888888889] for min, max and average temperature observations
## For start api example "/api/v1.0/2016-08-23<br/>" the return results in the api url page is [58.0, 87.0, 74.59058295964125] for min, max and average temperature observations
## In order to return min, max and average statistics you have to enter dates in initial homepage app route.

if __name__ == "__main__":
    app.run(debug=True)