# Import the dependencies.
from flask import Flask, jsonify, request
import numpy as np
import datetime as dt
from datetime import timedelta
from datetime import datetime

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
Base.prepare(autoload_with=engine)

# Save reference to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB

session = Session(engine)
Base.metadata.create_all(engine)
#################################################
# Flask Setup
#################################################

app = Flask(__name__)


#################################################
# Flask Routes
#################################################

    # List all available routes at 'home' page 
@app.route("/")
def home():
    print("heading to the home page")
    return(
        f"Welcome to the Hawaii Climate API!<br/>"
        f"Available routes:<br>"
        f"/api/v1.0/precipitation<br/> "
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/> "
        f"/api/v1.0/start<br/>" 
        f"/api/v1.0/start/end<br/>"
        f"Enter Date as 'YYYY-MM-DD' in place of 'start' and/or 'end'.<br/>"
    )


# Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value.
       # Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def precipitation():
    print("Precipitation Page Loading . . . ")
    """Precipitation Date for the Last Year"""  
        #Year of Info
    end_date = dt.date(2017, 8, 23)
    start_date = end_date - dt.timedelta(days=365)
    
        # query results from your precipitation analysis, 12 months of data, to a dictionary
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= start_date, Measurement.date <= end_date).all()
    session.close()
    
        #Dictionary using date as the key and prcp as the value, JSONIFY
    p_results = {date: prcp for date, prcp in precipitation}
    return jsonify(p_results)


#Return a JSON list of stations from the dataset
@app.route("/api/v1.0/stations")
def stations():
    print("All Stations' Information")
       # Query all stations
    results = session.query(Station.name).all()
    session.close()

    #Return a JSON list of stations from the dataset.
    all_stations = list(np.ravel(results))
    return jsonify(all_stations)


#Query the dates and temperature observations of the most-active station for the previous year of data.    
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
        #find the most active station
    most_active = session.query(Measurement.station, func.count(Measurement.station)).\
    group_by(Measurement.station).\
    order_by(func.count(Measurement.station).desc()).all()
    
    #set most active station as index 0
    most_active_station = most_active[0]

    # Query the last 12 months of temperature observation data for this station
    yr_temps = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == most_active_station, Measurement.date >= start_date, Measurement.date <= most_recent).all()

    # Extract temperature data into a list
    temperatures = [temp for date, temp in yr_temps]
    
    #Return a JSON list of temperature observations for the previous year. 
    temp_obs = [{"date": date, "temperature": temp} for date, temp in yr_temps]

    # Return the JSON response
    return jsonify(temp_obs)


#Start Date Provided in URL
@app.route('/api/v1.0/<start>')
def get_temp_stats(start):
    print(f"Start Date provided. Loading Temperatures.")
    session = Session(engine)
    
    # Validate and parse the start date
    try:
        start_date = datetime.strptime(start, '%Y-%m-%d')
    except ValueError:
        return jsonify({"error": "Invalid start date format. Use YYYY-MM-DD."}), 400

    # Query the database for temperature statistics
    temperature_stats=session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()
    
    
    # Create a dictionary with temperature statistics
    temperature_data = {
        "start_date": start_date.strftime('%Y-%m-%d'),
        "TMIN": temperature_stats[0][0],
        "TAVG": temperature_stats[0][1],
        "TMAX": temperature_stats[0][2]
    }
    session.close()
    # Return the JSON response
    return jsonify(temperature_data)



#For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date, inclusive.
@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    print(f"Start and End Dates provided. Loading Temperatures.")
    session = Session(engine)
    start_date = dt.datetime.strptime(start,'%Y-%m-%d')
    end_date = dt.datetime.strptime(end,'%Y-%m-%d')
    
    temperature_stats=session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter((Measurement.date>=start_date),(Measurement.date<=end_date)).all()
    
    if not temperature_stats:
        return jsonify({"error": "No data found for the specified date range."}), 404

    
    # Create a dictionary with temperature statistics
    temperature_data = {
        "start_date": start_date.strftime('%Y-%m-%d'), 
        "end_date": end_date.strptime(end,'%Y-%m-%d'),
        "TMIN": temperature_stats[0][0],
        "TAVG": temperature_stats[0][1],
        "TMAX": temperature_stats[0][2]
    }
        
    session.close()
    # Return the JSON response
    return jsonify(temperature_data)


if __name__ == "__main__":
    app.run(debug=True)   
    
