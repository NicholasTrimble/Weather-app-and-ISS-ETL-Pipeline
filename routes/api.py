from flask import Blueprint, jsonify
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
from Main import fetch_iss_position


api_bp = Blueprint("api", __name__)
load_dotenv()

NEWS_API_KEY = os.getenv("API_KEY_NEWSAPI")
WEATHER_API_KEY = os.getenv("API_KEY_OPENWEATHER")

@api_bp.route("/news")
def get_news():
    city = request.args.get("city")
    if not city:
        return jsonify({"headlines": ["No city provided."]})

    news_url = "https://newsapi.org/v2/everything"
    params = {
        "q": city,
        "sortBy": "publishedAt",
        "language": "en",
        "pageSize": 5,
        "apiKey": NEWS_API_KEY
    }

    try:
        response = requests.get(news_url, params=params, timeout=10)
        response.raise_for_status() 
        data = response.json()
        
        if data.get("status") != "ok":
            print("NewsAPI error:", data)
            return jsonify({"headlines": ["Error fetching news from NewsAPI."]})

        articles = data.get("articles", [])
        headlines = [article["title"] for article in articles]
        if not headlines:
            headlines = ["No recent news found for this city."]
        return jsonify({"headlines": headlines})

    except Exception as e:
        print("Exception in /news route:", e)
        return jsonify({"headlines": ["Error fetching news."]})

@api_bp.route("/subscribe", methods=["POST"])
def subscribe():
    email = request.form.get("email")
    if email:
        add_user(email)
    return redirect("/")


@api_bp.route("/iss_position")
def iss_position():
    latitude, longitude, timestamp = fetch_iss_position()
    return jsonify({
        "latitude": latitude,
        "longitude": longitude,
        "timestamp": timestamp
    })

@api_bp.route("/weather_info")
def weather_info_route():
    # Get latitude and longitude from query parameters
    lat = round(float(request.args.get("lat", 51.507351)), 4)  # default London
    lon = round(float(request.args.get("lon", -0.127758)), 4)

    # Determine if it’s night (optional, default True for now)
    is_night_time = True

    # Call weather helper to get full weather info
    weather_info = get_weather_data(lat, lon, is_night_time)

    # Return JSON for JS to read
    return jsonify(weather_info)


@api_bp.route("/star_chart")
def star_chart():
    from flask import request, jsonify

    lat = request.args.get("lat")
    lon = request.args.get("lon")

    if not lat or not lon:
        return jsonify({"error": "Missing lat/lon"}), 400

    try:
        # note the module prefix
        image_url = astronomy_api.generate_star_chart(float(lat), float(lon))
        return jsonify({"imageUrl": image_url})
    except Exception as e:
        print("Star chart error:", e)
        return jsonify({"error": str(e)}), 500



@api_bp.route("/unsubscribe")
def unsubscribe():
    email = request.args.get("email")
    if email:
        remove_user(email)
        return f"Email {email} has been unsubscribed."
    return "No email provided."


@api_bp.route("/forecast")
def get_forecast():
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    
    url = f"http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=imperial"
    
    response = requests.get(url)
    return jsonify(response.json())