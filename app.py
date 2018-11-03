from flask import Flask, jsonify

import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

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
        f"/api/v1.0/precipitation/<date><br/>"
        f"/api/v1.0/passengers"
    )

@app.route("/api/v1.0/precipitation/<date>")
def precipitation(date):
    """
    Convert the query results to a Dictionary using date as the key and prcp as the value.    
    Return the JSON representation of your dictionary.
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




if __name__ == "__main__":
    app.run(debug=True)


# 

# 

# 

# 
# /api/v1.0/tobs
# 
# query for the dates and temperature observations from a year from the last data point.
# Return a JSON list of Temperature Observations (tobs) for the previous year.
# 
# 
# 
# /api/v1.0/<start> and /api/v1.0/<start>/<end>
# 
# 
# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
# When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
# 
# 
# 
# 
# 
# Hints
# 
# 
# You will need to join the station and measurement tables for some of the analysis queries.
# Use Flask jsonify to convert your API data into a valid JSON response object.