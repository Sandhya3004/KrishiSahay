#!/usr/bin/env python3
"""
Weather Agent for KrishiSahay
Provides weather data and proactive alerts.
Uses OpenWeatherMap API if key is present, otherwise realistic mock data.
"""

import requests
import json
import os
from datetime import datetime, timedelta
import random
from dotenv import load_dotenv

load_dotenv()

class WeatherAgent:
    def __init__(self):
        self.api_key = os.getenv("WEATHER_API_KEY", "")
        self.base_url = "http://api.openweathermap.org/data/2.5"
        
        # Realistic base weather for Indian districts (mock mode)
        self.location_climate = {
            "Agra": {"temp_range": (25, 35), "humidity_range": (40, 60), "conditions": ["clear sky", "haze", "few clouds"]},
            "Delhi": {"temp_range": (20, 38), "humidity_range": (30, 70), "conditions": ["clear sky", "smoke", "mist"]},
            "Mumbai": {"temp_range": (24, 32), "humidity_range": (70, 90), "conditions": ["haze", "light rain", "moderate rain"]},
            "Chennai": {"temp_range": (26, 36), "humidity_range": (65, 85), "conditions": ["clear sky", "few clouds", "light rain"]},
            "Kolkata": {"temp_range": (24, 34), "humidity_range": (60, 85), "conditions": ["mist", "light rain", "clear sky"]},
            "Bangalore": {"temp_range": (18, 28), "humidity_range": (50, 80), "conditions": ["clear sky", "few clouds", "light drizzle"]},
            "Hyderabad": {"temp_range": (22, 34), "humidity_range": (40, 70), "conditions": ["clear sky", "haze", "few clouds"]},
            "Pune": {"temp_range": (20, 32), "humidity_range": (45, 75), "conditions": ["clear sky", "few clouds", "haze"]},
            "Lucknow": {"temp_range": (22, 36), "humidity_range": (35, 65), "conditions": ["clear sky", "haze", "mist"]},
            "Jaipur": {"temp_range": (24, 38), "humidity_range": (25, 55), "conditions": ["clear sky", "haze", "dust"]}
        }
        self.default_climate = {"temp_range": (22, 34), "humidity_range": (40, 70), "conditions": ["clear sky", "few clouds", "haze"]}

    def get_weather(self, location):
        """Return weather data – real API if key present, else realistic mock."""
        if self.api_key:
            try:
                return self._get_real_weather(location)
            except Exception as e:
                print(f"Real weather API failed: {e}. Falling back to mock.")
                return self._get_mock_weather(location)
        else:
            return self._get_mock_weather(location)

    def _get_real_weather(self, location):
        """Fetch real weather data from OpenWeatherMap."""
        # Current weather
        current_url = f"{self.base_url}/weather"
        current_params = {
            "q": f"{location},IN",
            "appid": self.api_key,
            "units": "metric"
        }
        current_resp = requests.get(current_url, params=current_params, timeout=10)
        current_resp.raise_for_status()
        current_data = current_resp.json()

        # 5-day forecast (3-hour intervals) – we'll take next 4 entries (~12 hours)
        forecast_url = f"{self.base_url}/forecast"
        forecast_params = {
            "q": f"{location},IN",
            "appid": self.api_key,
            "units": "metric",
            "cnt": 8   # 8 intervals = 24 hours
        }
        forecast_resp = requests.get(forecast_url, params=forecast_params, timeout=10)
        forecast_resp.raise_for_status()
        forecast_data = forecast_resp.json()

        # Parse current
        weather = current_data["weather"][0]["description"]
        temp = current_data["main"]["temp"]
        humidity = current_data["main"]["humidity"]
        wind_speed = current_data["wind"]["speed"]
        rain = current_data.get("rain", {}).get("1h", 0)

        # Parse forecast (next 4 entries ~12 hours)
        forecast = []
        for item in forecast_data["list"][:4]:
            forecast.append({
                "time": item["dt_txt"],
                "temp": item["main"]["temp"],
                "humidity": item["main"]["humidity"],
                "description": item["weather"][0]["description"],
                "rain": item.get("rain", {}).get("3h", 0)
            })

        return {
            "location": location,
            "current": {
                "temp": temp,
                "humidity": humidity,
                "description": weather,
                "wind_speed": wind_speed,
                "rain": rain
            },
            "forecast": forecast,
            "is_mock": False
        }

    def _get_mock_weather(self, location):
        """Return location‑specific mock weather, consistent for each call."""
        # Use climate data for the given location or default
        climate = self.location_climate.get(location, self.default_climate)
        
        # Generate values within the typical range (deterministic based on location + today's date)
        seed = hash(f"{location}_{datetime.now().strftime('%Y%m%d')}")
        random.seed(seed)
        
        temp = random.randint(*climate["temp_range"])
        humidity = random.randint(*climate["humidity_range"])
        condition = random.choice(climate["conditions"])
        wind_speed = random.randint(5, 25)
        rain = random.randint(0, 5) if "rain" in condition else 0
        
        # Forecast for next few hours (slight variations)
        forecast = []
        for i in range(1, 5):
            hour_delta = i * 3
            forecast.append({
                "time": (datetime.now() + timedelta(hours=hour_delta)).strftime("%Y-%m-%d %H:%M:%S"),
                "temp": temp + random.randint(-2, 2),
                "humidity": humidity + random.randint(-5, 5),
                "description": random.choice(climate["conditions"]),
                "rain": random.randint(0, 3) if "rain" in condition else 0
            })
        
        return {
            "location": location,
            "current": {
                "temp": temp,
                "humidity": humidity,
                "description": condition,
                "wind_speed": wind_speed,
                "rain": rain
            },
            "forecast": forecast,
            "is_mock": True
        }

    def generate_alerts(self, weather_data, crop=None):
        """Generate proactive alerts based on weather data."""
        alerts = []
        current = weather_data.get("current", {})
        
        # Rain alert
        if current.get("rain", 0) > 0:
            alerts.append({
                "type": "rain",
                "severity": "info",
                "icon": "🌧️",
                "title": "बारिश की सूचना",
                "message": f"अभी बारिश हो रही है ({current['rain']} mm/h)।",
                "advice": "अगर छिड़काव नहीं किया है, तो बारिश रुकने तक प्रतीक्षा करें।"
            })
        
        # Forecast rain
        for f in weather_data.get("forecast", []):
            if f.get("rain", 0) > 0:
                alerts.append({
                    "type": "forecast_rain",
                    "severity": "warning",
                    "icon": "⚠️",
                    "title": "बारिश की संभावना",
                    "message": f"अगले कुछ घंटों में बारिश हो सकती है।",
                    "advice": "कीटनाशक या उर्वरक का छिड़काव टालें।"
                })
                break
        
        # Temperature alerts
        temp = current.get("temp", 25)
        if temp > 35:
            alerts.append({
                "type": "heat",
                "severity": "warning",
                "icon": "🔥",
                "title": "भीषण गर्मी",
                "message": f"तापमान बहुत अधिक है ({temp}°C)।",
                "advice": "फसलों में पानी की कमी हो सकती है। सिंचाई करें।"
            })
        elif temp < 10:
            alerts.append({
                "type": "cold",
                "severity": "warning",
                "icon": "❄️",
                "title": "कड़ाके की ठंड",
                "message": f"तापमान कम है ({temp}°C)। पाले का खतरा।",
                "advice": "रात में हल्का पानी का छिड़काव करें या फसलों को ढकें।"
            })
        
        # Humidity alerts
        humidity = current.get("humidity", 50)
        if humidity > 85:
            alerts.append({
                "type": "high_humidity",
                "severity": "info",
                "icon": "💧",
                "title": "उच्च नमी",
                "message": f"नमी बहुत अधिक है ({humidity}%)।",
                "advice": "फफूंद रोगों का खतरा बढ़ सकता है। फसलों की नियमित जांच करें।"
            })
        
        # Crop‑specific alerts (example)
        if crop:
            crop_lower = crop.lower()
            if "गेहूं" in crop_lower or "wheat" in crop_lower:
                if temp > 32:
                    alerts.append({
                        "type": "crop_heat_stress",
                        "severity": "warning",
                        "icon": "🌾",
                        "title": "गेहूं के लिए सावधानी",
                        "message": "अधिक तापमान गेहूं के दाने भरने को प्रभावित कर सकता है।",
                        "advice": "हल्की सिंचाई करें।"
                    })
            elif "सरसों" in crop_lower or "mustard" in crop_lower:
                if humidity > 70:
                    alerts.append({
                        "type": "crop_pest_risk",
                        "severity": "info",
                        "icon": "🌿",
                        "title": "सरसों में कीट का खतरा",
                        "message": "अधिक नमी से कीटों का खतरा बढ़ सकता है।",
                        "advice": "माहू कीट की नियमित जांच करें।"
                    })
        return alerts