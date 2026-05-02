from flask import Blueprint, render_template
import datetime
from zoneinfo import ZoneInfo
from Main import fetch_iss_position
from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
from database import add_user, remove_user
from utils.weather_helpers import get_weather_data, calculate_visibility
import os
from dotenv import load_dotenv
import utils.astronomy_api as astronomy_api
import requests



ui_bp = Blueprint("ui", __name__)

DB_NAME = "iss_pipeline.db"

@ui_bp.route("/")
def home():
    return render_template("home.html")

@ui_bp.route("/map")
def show_map():
    return render_template("map.html")


@ui_bp.route("/data")
def show_data():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM iss_data ORDER BY timestamp DESC LIMIT 10")
    rows = cursor.fetchall()
    conn.close()

    return render_template("data.html", rows=rows)