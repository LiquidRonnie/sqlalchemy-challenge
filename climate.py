# Climate app
# Import Depenedcies
import pandas as pd
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from sqlalchemy import and_

#import Flask
from flask import Flask, jsonify, redirect

############################################################
############################################################

# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# Declare automap base
Base = automap_base()
conn = engine.connect()
# reflect an existing database into a new model
Base.prepare(engine, reflect=True)
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create our session (link) from Python to the DB
session = Session(engine)

############################################################
############################################################

# create an app.

app = Flask(__name__)

# Define routes

@app.route("/")
def home():
    return (
        f"Welcome to our climate app! Here are our API options.<br><br>"
        f"/api/v1.0/precipitation<br>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/[start_date format:yyyy-mm-dd] <br>"
        f"/api/v1.0/[start_date format:yyyy-mm-dd]/[end_date format:yyyy-mm-dd]"
    )

# Convert the query results to a dictionary using date as the key and prcp as the value.
# Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def precipitation():
    prcpt = session.query(Measurement.date,Measurement.station, Measurement.prcp).all()

    session.close()

    prcp_year = []
    for station, date, prcp in prcpt:
        year_dict = {}
        year_dict["date"] = station
        year_dict["station"] = date
        year_dict["prcp"] = prcp
        prcp_year.append(year_dict)

    prp_list = list(np.ravel(prcp_year))

    return jsonify(prp_list)

# Query restuls for all stattions and Jsonify 
@app.route("/api/v1.0/stations")
def stations():

    stations = session.query(Station.station).all()
    
    session.close()

    all_stations = list(np.ravel(stations))

    return jsonify(all_stations)

# Query the dates and temperature observations of the most active station for the last year of data.
# Return a JSON list of temperature observations (TOBS) for the previous year.

@app.route("/api/v1.0/tobs")
def tobs():
    # Query the dates and temperature observations of the most active station for the last year of data.

    year_hist = session.query(Measurement.station, Measurement.date, Measurement.tobs).filter(
    and_(Measurement.station =='USC00519281', Measurement.date >= '2016-08-23')).all()

    session.close()

    tobs_list = []
    for station, date, tobs in year_hist:
        tobs_dict = {}
        tobs_dict['station'] = station
        tobs_dict['date'] = date
        tobs_dict['tobs'] = tobs

        tobs_list.append(tobs_dict)

    temp_list = list(np.ravel(tobs_list))

    return jsonify(temp_list)


# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.

@app.route("/api/v1.0/<start>")
def start_date(start):
    begin_date = dt.datetime.strptime(start,'%Y-%m-%d')

    functions = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.round(func.avg(Measurement.tobs),2)).\
        filter(Measurement.date >= start).all()

    session.close()

    start_year = []
    for min, max, avg in functions:
        start_date_dict = {}
        start_date_dict['min'] = min
        start_date_dict['max'] = max
        start_date_dict['avg'] = avg

        start_year.append(start_date_dict)

    date = list(np.ravel(start_year))

    return jsonify(date)

# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.

@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):

    intial_date = dt.datetime.strptime(start,'%Y-%m-%d')
    end_date = dt.datetime.strptime(end,'%Y-%m-%d')

    start_end_functions = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.round(func.avg(Measurement.tobs))).\
	    filter(Measurement.date.between(start,end)).all()

    session.close()

    start_end = []
    for min, max, avg in start_end_functions:
        start_end_dict = {}
        start_end_dict['min'] = min
        start_end_dict['max'] = max
        start_end_dict['avg'] = avg

        start_end.append(start_end_dict)

    start_end_dates = list(np.ravel(start_end))

    return jsonify(start_end_dates)


if __name__ == '__main__':
    app.run(debug=True)