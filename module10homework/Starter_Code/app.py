# Import the dependencies.
from flask import Flask, jsonify
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import datetime as dt
import numpy as np


#################################################
# Database Setup
#################################################
engine = create_engine('sqlite:///Resources/hawaii.sqlite')


# reflect an existing database into a new model
base = automap_base()
# reflect the tables
base.prepare(engine, reflect=True)

# Save references to each table
measurement = base.classes.measurement
station = base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route('/')

def welcome():
    'List all available API routes.'
    return """
    Available Routes:
    /api/v1.0/precipitation
    /api/v1.0/stations
    /api/v1.0/tobs
    /api/v1.0/&lt;start&gt;
    /api/v1.0/&lt;start&gt;/&lt;end&gt;
    """

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    most_recent = session.query(func.max(measurement.date)).scalar()
    one_year = dt.datetime.strptime(most_recent, "%Y-%m-%d") - dt.timedelta(days=365)


    results = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date >= one_year).all()
    session.close()

    precipitation_dict = {date: prcp for date, prcp in results}
    return jsonify(precipitation_dict)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(station.station).all()
    session.close()

    stations_list = list(np.ravel(results))
    return jsonify(stations=stations_list)

@app.route('/api/v1.0/tobs')
def tobs():
    session = Session(engine)
    most_recent = session.query(func.max(measurement.date)).scalar()
    one_year = dt.datetime.strptime(most_recent, "%Y-%m-%d") - dt.timedelta(days=365)

    most_active_id = session.query(measurement.station).\
                    group_by(measurement.station).\
                    order_by(func.count(measurement.id).desc()).first()[0]

    results = session.query(measurement.date, measurement.tobs).\
                filter(measurement.station == most_active_id).\
                filter(measurement.date >= one_year).all()
    session.close()
    
    tobs_data = [{'date': result[0], 'tobs': result[1]} for result in results]

    return jsonify({'station': most_active_id, 'tobs': tobs_data})

@app.route("/api/v1.0/&lt;start&gt;/&lt;end&gt;")
def temp_stats(start, end=None):
    session = Session(engine)

    if end is None:
        end = session.query(func.max(measurement.date)).scalar()

        start_date = dt.datetime.strptime(start, '%Y-%m-%d')
        end_date = dt.datetime.strptime(end, '%Y-%m-%d')

        selection = [func.min(measurment.tobs), func.avg(measurement.tobs), func.max(measurements.tobs)]
        results = session.query(*sel).filter(measurement.date >= start_date, measurement.date <= end_date).all()
        session.close()

        temp_data = {
            'TempMIN': results [0][0],
            'TempAVG': results[0][1],
            'TempMAX': results[0][2]
        }

        return jsonify(temp_data)

if __name__ == '__main__':
    app.run(debug=True)