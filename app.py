from flask import Flask, jsonify

import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)


#########################
# Flask set-up
#########################
app = Flask(__name__)

#########################
# Flask Routes
#########################

@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation/date<br/>"
        f"/api/v1.0/stations"
    )

@app.route("/api/v1.0/precipitation/<date>")
def precipitation(date):
    """    
    Convert the query results to a Dictionary using date as the key and prcp as the value.    
    Return the JSON representation of your dictionary.
    exemple: http://127.0.0.1:5000/api/v1.0/precipitation/2017-07-15
    """
    
    dico = {date: session.query(Measurement.prcp).filter( Measurement.date == date).all()}       
    
    return jsonify(dico)

@app.route("/api/v1.0/stations")
def stations():
    """
    Return a JSON list of stations from the dataset.
    """
    # I did not find a way to query all the fields of the reflected table
    # I REALLY wish we had some kind of powerpoint or cheat-sheet to help us with the syntax!!!
    q = session.query(Station.station, Station.name,  Station.latitude,  Station.longitude, Station.elevation).all()
    
#     print(q )
    return jsonify(q)

@app.route("/api/v1.0/tobs")
def tobs():
    """
    # query for the dates and temperature observations from a year from the last data point.
    # Return a JSON list of Temperature Observations (tobs) for the previous year.
    """
    # Calculate the date 1 year ago from the last data point in the database
    latest_date = session.query(Measurement.date).\
                order_by(Measurement.date.desc()).\
                first()
    # converting the string into datetime
    dt_latest_date = dt.datetime.strptime(latest_date.date, '%Y-%m-%d')
    # Calculating the date from 12 months before
    year_before = dt_latest_date - dt.timedelta(days=365) #20) #365)

    # Perform a query to retrieve the data and precipitation scores
    prcp_last12m = session.query(Measurement.date, Measurement.prcp).\
                    filter( Measurement.date >= year_before).all()
    return jsonify(prcp_last12m)


@app.route("/api/v1.0/<start_date>")
def start_only(start_date):
    """
    # Return a JSON list of the minimum temperature, the average temperature, 
    # and the max temperature for a given start or start-end range.
    # When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
    
    http://127.0.0.1:5000/api/v1.0/2017-07-15
    """
    end_date = session.query(Measurement.date).\
            order_by(Measurement.date.desc()).first()[0]

    return jsonify(range_normals(start_date, end_date))

@app.route("/api/v1.0/<start_date>/<end_date>")
def start_end(start_date, end_date): #=None):
    """
    # Return a JSON list of the minimum temperature, the average temperature, 
    # and the max temperature for a given start or start-end range.
    # When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
     example: http://127.0.0.1:5000/api/v1.0/2017-07-15/2017-07-30

    """
     
     
    return jsonify(range_normals(start_date, end_date))


def range_normals(trip_start, trip_end):
    """Range_normals
    
    Args:
        trip_start (str): A date string in the format '%yyyy-%m-%d'
        trip_end (str): A date string in the format '%yyyy-%m-%d'        
         
    Returns:
        A list of tuples containing the daily normals, tmin, tavg, and tmax
    
    """
    
    # create the list of dates between trip_start and trip_end
    d1 = dt.date(int(trip_start[0:4]), int(trip_start[5:7]), int(trip_start[8:]))  # start date
    d2 = dt.date(int(trip_end[0:4]), int(trip_end[5:7]), int(trip_end[8:]))   # end date
    delta = d2 - d1         # timedelta
    trip_dates = [d1 + dt.timedelta(ii) for ii in range(delta.days + 1)]
    
    # calculate the normals for theses dates
    normals = [daily_normals(str(dd)[5:]) for dd in trip_dates ]
    
    
    return normals
# 
# 
def daily_normals(date):
    """Daily Normals.
     
    Args:
        date (str): A date string in the format '%m-%d'
         
    Returns:
        A list of tuples containing the daily normals, tmin, tavg, and tmax
     
    """
     
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    return session.query(*sel).filter(func.strftime("%m-%d", Measurement.date) == date).all()




if __name__ == "__main__":
    app.run(debug=True)
