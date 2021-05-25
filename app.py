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
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

@app.route("/api/v1.0/precipitation")
def prcp():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Calculate the date one year from the last date in data set.
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days = 365)

    # Query to retrieve the data and precipitation scores
    results_prcp = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= query_date).order_by(Measurement.date).all()

    session.close()

    # Create a dictionary of all precip data
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

    # Query to retrieve list of stations
    query_station = session.query(Station.station, Station.name).all()
    
    session.close()

    # Create a list of stations
    station_data = list(np.ravel(query_station))

    return jsonify(station_data)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query to retrieve most active station and tobs data    
    query_date = dt.date(2017, 8, 23) - dt.timedelta(days = 365)

    active_station = session.query(Measurement.date, (Measurement.tobs)).\
        filter(Measurement.date >= query_date).\
        filter(Measurement.station == 'USC00519281').\
        order_by(Measurement.date).all()
    
    session.close()

    # Create a list from the data of all tobs data
    tobs_data = list(np.ravel(active_station))

    return jsonify(tobs_data)

@app.route("/api/v1.0/<start>")
def start_date(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Define Start set up
    start_date = dt.datetime.strptime(start, '%m-%d-%Y')
           
    # Query for data from the user defined start date
    temp =[func.min(Measurement.tobs), 
        func.avg(Measurement.tobs), 
        func.max(Measurement.tobs)]
    
    query_temp = session.query(*temp).\
        filter(Measurement.date >= start_date).all()
    
    session.close()

    # Convert list of tuples into normal list
    start_date_data = list(np.ravel(query_temp))

    return jsonify(start_date_data)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start,end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Define Start & End set up 
    start_date = dt.datetime.strptime(start, '%m-%d-%Y')
    end_date = dt.datetime.strptime(end, '%m-%d-%Y')
           
    # Query for data from the user defined start date
    temp =[func.min(Measurement.tobs), 
        func.avg(Measurement.tobs), 
        func.max(Measurement.tobs)]
    
    query_temp = session.query(*temp).\
        filter(Measurement.date >= start_date).\
        filter(Measurement.date <= end_date).all()
    
    session.close()

    # Convert list of tuples into normal list
    start_end_data = list(np.ravel(query_temp))

    return jsonify(start_end_data)

if __name__ == '__main__':
    app.run(debug=True)

