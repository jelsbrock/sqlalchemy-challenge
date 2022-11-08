import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

Base = automap_base()

Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

app = Flask(__name__)

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= '2016-08-23').all()

    session.close()

    prcp_by_date = []
    for date, prcp in results:
        prcp_data = {}
        prcp_data["date"] = date
        prcp_data["prcp"] = prcp
        prcp_by_date.append(prcp_data)

    return jsonify(prcp_by_date)

@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    results = session.query(Measurement.station).group_by(Measurement.station).all()
    station_list = list(np.ravel(results))

    session.close()

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= '2016-08-23').filter(Measurement.station == 'USC00519281').all()
    temp_list = list(np.ravel(results))

    session.close()

    return jsonify(temp_list)

@app.route("/api/v1.0/<start>")
def start_date(start):

    session = Session(engine)

    temps = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    
    session.close()

    start_filter = session.query(*temps).filter(Measurement.date >= start).all()
    
    start_list = [
        {"TMIN": start_filter[0][0]},
        {"TAVG": start_filter[0][1]},
        {"TMAX": start_filter[0][2]}
    ]

    if start <= '2017-08-23':
        return jsonify(start_list)
    else:
        return jsonify("Error: date not in range")

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):

    session = Session(engine)

    temps = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    
    session.close()
    
    start_end_filter = session.query(*temps).\
        filter(Measurement.date.between(start,end)).all()
   
    start_end_list = [
        {"TMIN": start_end_filter[0][0]},
        {"TAVG": start_end_filter[0][1]},
        {"TMAX": start_end_filter[0][2]}
    ]

    if (start <= '2017-08-23') and (end >='2010-01-01'):
        return jsonify(start_end_list)
    else:
        return jsonify("Error: one or both dates not in range")

app.run(debug=True)
