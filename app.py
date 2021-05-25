#################################################
# Imports
#################################################
import numpy as np
import pandas as pd
import datetime as dt
from dateutil.relativedelta import relativedelta

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
base = declarative_base()

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/startdate<br/>"
        f"/api/v1.0/start_end_date<br/>"
    )

@app.route("/api/v1.0/precipitation")
def prcp():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Calculate the date one year from the last date in data set.
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days = 365)

    # Perform a query to retrieve the data and precipitation scores
    results_prcp = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= query_date).order_by(Measurement.date).all()

    session.close()

    # Create a dictionary from the row data and append to a list of all precip data
    prcp_data = []
    for date, prcp in results_prcp:
        prcp_dict = {}
        prcp_dict["Date"] = date
        prcp_dict["Precipitation"] = prcp
        prcp_data.append(prcp_dict)

    return jsonify(prcp_data)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query list of stations
    query_station = session.query(Station.station, Station.name).all()
    
    session.close()

    # Create a list of stations
    station_data = list(np.ravel(query_station))

    return jsonify(station_data)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query most active station and tobs data    
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days = 365)

    active_station = session.query(Measurement.date, (Measurement.tobs)).\
        filter(Measurement.date >= query_date).\
        filter(Measurement.station == 'USC00519281').\
        order_by(Measurement.date).all()
    
    session.close()

    # Create a list from the data of all tobs data
    tobs_data = list(np.ravel(active_station))

    return jsonify(tobs_data)

@app.route("/api/v1.0/startdate")
def startdate(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    start = dt.datetime.strptime(start, '%m-%d-%Y')
       
    # Query for data from the user defined start date

    inter=[func.min(Measurement.tobs),func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    results=session.query(*inter).\
        filter(Measurement.date>=start).all()

    session.close()

    # Convert list of tuples into normal list
    startdate = list(np.ravel(results))

    return jsonify(startdate)


@app.route("/api/v1.0/start_end_date")
def startend(start,end):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    start = dt.datetime.strptime(start, '%m-%d-%Y')
    end = dt.datetime.strptime(end, '%m-%d-%Y')   
    
    # Query for data from the user defined start and end dates
    inter=[func.min(Measurement.tobs),func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    results=session.query(*inter).\
        filter(Measurement.date>=start).filter(Measurement.date<=end).all()

    session.close()

    # Convert list of tuples into normal list
    startend = list(np.ravel(results))
    
    return jsonify(startend)

if __name__ == '__main__':
    app.run(debug=True)

