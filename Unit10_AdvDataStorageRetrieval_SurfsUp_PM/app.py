import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Viewing all of the classes that automap found
Base.classes.keys()

# Save reference to the table
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

@app.route("/")
def home():
    """List all available api routes."""
    return (
        f"Home Page<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Convert the query results to a Dictionary using date as the key and prcp as the value"""

    prcp_date = session.query(Measurement).order_by(Measurement.date.desc()).limit(1)

    for value in prcp_date:
        latest_date_value = value.date

    #Converting the date to from str format to date format to calculate the date 1 year ago

    converted_date = dt.datetime.strptime(latest_date_value, "%Y-%m-%d")

    # Calculate the date 1 year ago from the last data point in the database
    date_one_yearago = converted_date - dt.timedelta(days=365)

    # Perform a query to retrieve the date and precipitation scores
    prcp_data = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= date_one_yearago).order_by(Measurement.date).all()

    # Convert to dictionary
    def Convert(tup): 
        di = dict(tup) 
        return di 
    # Driver Code  
    # prcp_dict = {} 
    prcp_dict = Convert(prcp_data)
    return jsonify(prcp_dict)


@app.route("/api/v1.0/stations")
def stations():
    """Return a list of all stations as a list of JSON"""
    # Query all stations
    listofstations = session.query(Station.station, Station.name).all()

    # Create a list from the row data
    all_stations = []
    for station, name in listofstations:
        station_dict = {}
        station_dict["station"] = station
        station_dict["name"] = name
        all_stations.append(station_dict)

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return a list of all tobs for the most active station as a list of JSON"""
    # Query most active station
    
    station_list = session.query(Measurement.station, func.count('*')).group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    mostactive=station_list[0][0]
    # Query the last 12 months of temperature observation data for this station and plot the results as a histogram
    mostactive_latestdate = session.query(Measurement).filter(Measurement.station==mostactive).order_by(Measurement.date.desc()).limit(1)

    for value in mostactive_latestdate:
        latestdate = value.date

    #Converting the date to from str format to date format to calculate the date 1 year ago

    converted_activedate = dt.datetime.strptime(latestdate, "%Y-%m-%d")

    # Calculate the date 1 year ago from the last data point of the most active station in the database
    date_one_activeyear = converted_activedate - dt.timedelta(days=365)
    temp_data = session.query(Measurement.tobs).filter(Measurement.station==mostactive).filter(Measurement.date >= date_one_activeyear).order_by(Measurement.date).all()

    # Create a list from the row data
    all_tobs = []
    for tobs in temp_data:
        tobs_dict = {}
        tobs_dict["tobs"] = tobs
        all_tobs.append(tobs_dict)

    return jsonify(all_tobs)


@app.route("/api/v1.0/<start>")
def startdate(start):
    """Return a list of min, max, avg for a start and end date as a list of JSON"""
    def calc_temps_start(start_date):
        """TMIN, TAVG, and TMAX for a list of dates.
        
        Args:
            start_date (string): A date string in the format %Y-%m-%d

        Returns:
            TMIN, TAVE, and TMAX
        """
        
        return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start_date).all()

    all_tempstats = calc_temps_start(start)
    return jsonify(all_tempstats)


@app.route("/api/v1.0/<start>/<end>")
def daterange(start, end):
    """Return a list of min, max, avg for a start and end date as a list of JSON"""
    def calc_temps(start_date, end_date):
        """TMIN, TAVG, and TMAX for a list of dates.
        
        Args:
            start_date (string): A date string in the format %Y-%m-%d
            end_date (string): A date string in the format %Y-%m-%d
            
        Returns:
            TMIN, TAVE, and TMAX
        """
        
        return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    all_tempstats = calc_temps(start, end)
    return jsonify(all_tempstats)

if __name__ == '__main__':
    app.run(debug=True)
