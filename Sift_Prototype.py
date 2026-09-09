# ================================
# Name: Sift
# Description: a functional grocery price comparison and health rating application, used to consolidate grocery prices and health ratings from various Australian supermarkets into a single user-friendly interface
# Author: Safin and Patrick
# Version: 0.7.0 "Prototype"
# Last Updated: 2026-08-19 (YYYY/MM/DD)
# Update Notes: final refinement of the application, creating the final prototype and proof of concept
#
# Dependencies: as imported in script, some must be downloaded via pip install
# Requirements: functioning camera (built-in or external), internet connection, web browser installed
# ================================

import tkinter as tk
from tkinter import ttk
import psutil
import time
from PIL import Image, ImageTk
import uuid
import json
import os
import difflib
import requests
import io
import webbrowser
import threading
from urllib.parse import quote
import sys
import subprocess

os.environ['DYLD_LIBRARY_PATH'] = '/opt/homebrew/lib:' + os.environ.get('DYLD_LIBRARY_PATH', '') # set a dynamic default library for the following two imports; had issues with importing the cv2 and pyzbar libraries on macOS. this is a workaround to ensure the correct library paths are used. this implementation has no unwanted effect on windows devices

if os.path.exists('/usr/local/lib'):
    os.environ['DYLD_LIBRARY_PATH'] = '/usr/local/lib:' + os.environ['DYLD_LIBRARY_PATH']

import cv2
from pyzbar.pyzbar import decode

# === Theme setting with hardcoded HEX colour values for all theme modes ===
THEMES = {
    "light": {
        "bg": "#F2F2F7", "text": "#000000", "btn_bg": "#000000", "btn_txt": "#FFFFFF",
        "card_bg": "#FFFFFF", "accent": "#3A3A3C", "island": "#000000"
    },
    "dark": {
        "bg": "#201E21", "text": "#FFFFFF", "btn_bg": "#3A3A3C", "btn_txt": "#FFFFFF",
        "card_bg": "#2C2C2E", "accent": "#8E8E93", "island": "#000000"
    },
    "pro-duo-triteranopia": {
        "bg": "#E4F1FE", "text": "#2C3E50", "btn_bg": "#22A7F0", "btn_txt": "#FFFFFF",
        "card_bg": "#FFFFFF", "accent": "#1F3A60", "island": "#1F3A60"
    },
    "inverted": {
        "bg": "#0D0D08", "text": "#FFFFFF", "btn_bg": "#FFFFFF", "btn_txt": "#000000",
        "card_bg": "#151510", "accent": "#C5C5C1", "island": "#FFFFFF", "blue_txt": "#FF8500", "green_txt": "#CB38A6"
    }
}

# === Hardcoded grocery database. Each item includes an ID, name, variant, health rating, and a list of stores with their respective prices and unit prices. ===
GROCERY_DATABASE = [
    {
        "id": "avocado_each",
        "name": "Fresh Hass Avocado",
        "variant": "Single Piece",
        "health_rating": 5.0,
        "stores": [
            {"store": "ALDI", "price": 1.2, "unit_price": 1.2, "unit": "ea"},
            {"store": "Coles", "price": 1.8, "unit_price": 1.8, "unit": "ea"},
            {"store": "Woolworths", "price": 1.7, "unit_price": 1.7, "unit": "ea"},
            {"store": "IGA", "price": 2.1, "unit_price": 2.1, "unit": "ea"}
        ],
        "nutriments": {
            "energy_kj": 670,
            "fat_g": 15.0,
            "saturated_fat_g": 2.1,
            "sugars_g": 0.3,
            "proteins_g": 2.0,
            "salt_g": 0.01
        }
    },
    {
        "id": "bananas_1kg",
        "name": "Fresh Cavendish Bananas 1kg",
        "variant": "Yellow Whole",
        "health_rating": 5.0,
        "stores": [
            {
                "store": "ALDI",
                "price": 3.5,
                "unit_price": 0.35,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 4.0,
                "unit_price": 0.4,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 3.9,
                "unit_price": 0.39,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 4.5,
                "unit_price": 0.45,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 370,
            "fat_g": 0.3,
            "saturated_fat_g": 0.1,
            "sugars_g": 12.0,
            "proteins_g": 1.1,
            "salt_g": 0.0
        }
    },
    {
        "id": "pink_lady_apples_1kg",
        "name": "Fresh Pink Lady Apples 1kg",
        "variant": "Bagged",
        "health_rating": 5.0,
        "stores": [
            {
                "store": "ALDI",
                "price": 3.99,
                "unit_price": 0.4,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 4.5,
                "unit_price": 0.45,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 4.5,
                "unit_price": 0.45,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 4.9,
                "unit_price": 0.49,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 220,
            "fat_g": 0.1,
            "saturated_fat_g": 0.0,
            "sugars_g": 10.4,
            "proteins_g": 0.3,
            "salt_g": 0.0
        }
    },
    {
        "id": "strawberries_250g",
        "name": "Fresh Strawberries 250g",
        "variant": "Punnet",
        "health_rating": 5.0,
        "stores": [
            {
                "store": "ALDI",
                "price": 2.99,
                "unit_price": 1.2,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 3.5,
                "unit_price": 1.4,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 3.5,
                "unit_price": 1.4,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 3.99,
                "unit_price": 1.6,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 135,
            "fat_g": 0.3,
            "saturated_fat_g": 0.0,
            "sugars_g": 4.9,
            "proteins_g": 0.7,
            "salt_g": 0.0
        }
    },
    {
        "id": "washed_potatoes_2kg",
        "name": "Washed White Potatoes 2kg",
        "variant": "Bagged",
        "health_rating": 4.5,
        "stores": [
            {
                "store": "ALDI",
                "price": 3.49,
                "unit_price": 0.17,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 4.5,
                "unit_price": 0.23,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 4.0,
                "unit_price": 0.2,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 4.8,
                "unit_price": 0.24,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 320,
            "fat_g": 0.1,
            "saturated_fat_g": 0.0,
            "sugars_g": 0.6,
            "proteins_g": 2.0,
            "salt_g": 0.01
        }
    },
    {
        "id": "brown_onions_1kg",
        "name": "Brown Onions 1kg",
        "variant": "Net Bag",
        "health_rating": 5.0,
        "stores": [
            {
                "store": "ALDI",
                "price": 1.99,
                "unit_price": 0.2,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 2.5,
                "unit_price": 0.25,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 2.5,
                "unit_price": 0.25,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 2.8,
                "unit_price": 0.28,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 170,
            "fat_g": 0.1,
            "saturated_fat_g": 0.0,
            "sugars_g": 4.2,
            "proteins_g": 1.1,
            "salt_g": 0.01
        }
    },
    {
        "id": "truss_tomatoes_1kg",
        "name": "Truss Tomatoes 1kg",
        "variant": "Fresh Loose",
        "health_rating": 5.0,
        "stores": [
            {
                "store": "ALDI",
                "price": 4.9,
                "unit_price": 0.49,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 5.9,
                "unit_price": 0.59,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 5.5,
                "unit_price": 0.55,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 6.2,
                "unit_price": 0.62,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 75,
            "fat_g": 0.2,
            "saturated_fat_g": 0.0,
            "sugars_g": 2.6,
            "proteins_g": 0.9,
            "salt_g": 0.01
        }
    },
    {
        "id": "baby_spinach_120g",
        "name": "Baby Spinach Leaves 120g",
        "variant": "Pre-washed Bag",
        "health_rating": 5.0,
        "stores": [
            {
                "store": "ALDI",
                "price": 1.79,
                "unit_price": 1.49,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 2.2,
                "unit_price": 1.83,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 2.2,
                "unit_price": 1.83,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 2.5,
                "unit_price": 2.08,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 95,
            "fat_g": 0.4,
            "saturated_fat_g": 0.1,
            "sugars_g": 0.4,
            "proteins_g": 2.9,
            "salt_g": 0.2
        }
    },
    {
        "id": "carrots_1kg",
        "name": "Fresh Carrots 1kg",
        "variant": "Bagged",
        "health_rating": 5.0,
        "stores": [
            {
                "store": "ALDI",
                "price": 1.2,
                "unit_price": 0.12,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 1.5,
                "unit_price": 0.15,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 1.5,
                "unit_price": 0.15,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 1.8,
                "unit_price": 0.18,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 170,
            "fat_g": 0.2,
            "saturated_fat_g": 0.0,
            "sugars_g": 4.7,
            "proteins_g": 0.9,
            "salt_g": 0.17
        }
    },
    {
        "id": "broccoli_each",
        "name": "Fresh Broccoli",
        "variant": "Head",
        "health_rating": 5.0,
        "stores": [
            {
                "store": "ALDI",
                "price": 1.5,
                "unit_price": 1.5,
                "unit": "ea"
            },
            {
                "store": "Coles",
                "price": 1.9,
                "unit_price": 1.9,
                "unit": "ea"
            },
            {
                "store": "Woolworths",
                "price": 1.85,
                "unit_price": 1.85,
                "unit": "ea"
            },
            {
                "store": "IGA",
                "price": 2.2,
                "unit_price": 2.2,
                "unit": "ea"
            }
        ],
        "nutriments": {
            "energy_kj": 140,
            "fat_g": 0.4,
            "saturated_fat_g": 0.1,
            "sugars_g": 1.7,
            "proteins_g": 2.8,
            "salt_g": 0.08
        }
    },
    {
        "id": "beef_mince_500g",
        "name": "Premium Beef Mince 500g",
        "variant": "Lean 90%",
        "health_rating": 4.5,
        "stores": [
            {
                "store": "ALDI",
                "price": 7.5,
                "unit_price": 1.5,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 8.5,
                "unit_price": 1.7,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 8.5,
                "unit_price": 1.7,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 880,
            "fat_g": 10.0,
            "saturated_fat_g": 4.5,
            "sugars_g": 0.0,
            "proteins_g": 21.0,
            "salt_g": 0.15
        }
    },
    {
        "id": "chicken_breast_500g",
        "name": "Chicken Breast Fillets 500g",
        "variant": "Skinless Boneless",
        "health_rating": 5.0,
        "stores": [
            {
                "store": "ALDI",
                "price": 6.2,
                "unit_price": 1.24,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 7.25,
                "unit_price": 1.45,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 7.0,
                "unit_price": 1.4,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 7.8,
                "unit_price": 1.56,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 440,
            "fat_g": 1.5,
            "saturated_fat_g": 0.4,
            "sugars_g": 0.0,
            "proteins_g": 22.5,
            "salt_g": 0.12
        }
    },
    {
        "id": "pork_sausages_500g",
        "name": "Traditional Pork Sausages 500g",
        "variant": "Thick",
        "health_rating": 2.5,
        "stores": [
            {
                "store": "ALDI",
                "price": 4.99,
                "unit_price": 1.0,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 6.0,
                "unit_price": 1.2,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 6.0,
                "unit_price": 1.2,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 6.5,
                "unit_price": 1.3,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 1250,
            "fat_g": 24.0,
            "saturated_fat_g": 9.0,
            "sugars_g": 1.0,
            "proteins_g": 14.0,
            "salt_g": 1.8
        }
    },
    {
        "id": "tasmanian_salmon_300g",
        "name": "Fresh Tasmanian Salmon Fillets 300g",
        "variant": "Skin On",
        "health_rating": 5.0,
        "stores": [
            {
                "store": "ALDI",
                "price": 10.99,
                "unit_price": 3.66,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 13.0,
                "unit_price": 4.33,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 12.5,
                "unit_price": 4.17,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 13.8,
                "unit_price": 4.6,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 870,
            "fat_g": 13.0,
            "saturated_fat_g": 2.5,
            "sugars_g": 0.0,
            "proteins_g": 20.0,
            "salt_g": 0.1
        }
    },
    {
        "id": "middle_bacon_500g",
        "name": "Rindless Middle Bacon 500g",
        "variant": "Smoked",
        "health_rating": 2.0,
        "stores": [
            {
                "store": "ALDI",
                "price": 5.99,
                "unit_price": 1.2,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 7.5,
                "unit_price": 1.5,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 7.5,
                "unit_price": 1.5,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 8.2,
                "unit_price": 1.64,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 1150,
            "fat_g": 20.0,
            "saturated_fat_g": 7.5,
            "sugars_g": 0.5,
            "proteins_g": 16.0,
            "salt_g": 2.5
        }
    },
    {
        "id": "lamb_cutlets_400g",
        "name": "Australian Lamb Cutlets 400g",
        "variant": "Fresh",
        "health_rating": 4.0,
        "stores": [
            {
                "store": "Coles",
                "price": 16.0,
                "unit_price": 4.0,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 15.5,
                "unit_price": 3.88,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 17.2,
                "unit_price": 4.3,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 1100,
            "fat_g": 21.0,
            "saturated_fat_g": 9.5,
            "sugars_g": 0.0,
            "proteins_g": 18.0,
            "salt_g": 0.15
        }
    },
    {
        "id": "full_cream_milk_2l",
        "name": "Fresh Full Cream Milk 2L",
        "variant": "Standard homogenised",
        "health_rating": 4.0,
        "stores": [
            {
                "store": "ALDI",
                "price": 3.1,
                "unit_price": 0.16,
                "unit": "100ml"
            },
            {
                "store": "Coles",
                "price": 3.1,
                "unit_price": 0.16,
                "unit": "100ml"
            },
            {
                "store": "Woolworths",
                "price": 3.1,
                "unit_price": 0.16,
                "unit": "100ml"
            },
            {
                "store": "IGA",
                "price": 3.45,
                "unit_price": 0.17,
                "unit": "100ml"
            }
        ],
        "nutriments": {
            "energy_kj": 260,
            "fat_g": 3.4,
            "saturated_fat_g": 2.3,
            "sugars_g": 4.8,
            "proteins_g": 3.3,
            "salt_g": 0.1
        }
    },
    {
        "id": "greek_yogurt_1kg",
        "name": "Natural Greek Style Yogurt 1kg",
        "variant": "Full Cream",
        "health_rating": 4.5,
        "stores": [
            {
                "store": "ALDI",
                "price": 5.2,
                "unit_price": 0.52,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 6.0,
                "unit_price": 0.6,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 5.8,
                "unit_price": 0.58,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 400,
            "fat_g": 5.0,
            "saturated_fat_g": 3.3,
            "sugars_g": 4.0,
            "proteins_g": 9.0,
            "salt_g": 0.1
        }
    },
    {
        "id": "free_range_eggs_12pk",
        "name": "Free Range Large Eggs 12 Pack",
        "variant": "700g Total",
        "health_rating": 5.0,
        "stores": [
            {
                "store": "ALDI",
                "price": 4.95,
                "unit_price": 0.41,
                "unit": "ea"
            },
            {
                "store": "Coles",
                "price": 5.5,
                "unit_price": 0.46,
                "unit": "ea"
            },
            {
                "store": "Woolworths",
                "price": 5.4,
                "unit_price": 0.45,
                "unit": "ea"
            },
            {
                "store": "IGA",
                "price": 6.2,
                "unit_price": 0.52,
                "unit": "ea"
            }
        ],
        "nutriments": {
            "energy_kj": 600,
            "fat_g": 9.9,
            "saturated_fat_g": 3.1,
            "sugars_g": 0.3,
            "proteins_g": 12.5,
            "salt_g": 0.3
        }
    },
    {
        "id": "cheddar_cheese_block_500g",
        "name": "Tasty Cheddar Cheese Block 500g",
        "variant": "Aged Tasty",
        "health_rating": 3.0,
        "stores": [
            {
                "store": "ALDI",
                "price": 5.99,
                "unit_price": 1.2,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 7.0,
                "unit_price": 1.4,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 6.9,
                "unit_price": 1.38,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 7.5,
                "unit_price": 1.5,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 1700,
            "fat_g": 33.0,
            "saturated_fat_g": 21.0,
            "sugars_g": 0.1,
            "proteins_g": 25.0,
            "salt_g": 1.7
        }
    },
    {
        "id": "salted_butter_250g",
        "name": "Western Star Salted Butter 250g",
        "variant": "Traditional",
        "health_rating": 2.0,
        "stores": [
            {
                "store": "ALDI",
                "price": 3.8,
                "unit_price": 1.52,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 4.7,
                "unit_price": 1.88,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 4.7,
                "unit_price": 1.88,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 5.1,
                "unit_price": 2.04,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 3000,
            "fat_g": 81.0,
            "saturated_fat_g": 54.0,
            "sugars_g": 0.6,
            "proteins_g": 0.6,
            "salt_g": 1.5
        }
    },
    {
        "id": "bega_cheese_slices_500g",
        "name": "Bega Tasty Cheese Slices 500g",
        "variant": "24 Slices",
        "health_rating": 3.0,
        "stores": [
            {
                "store": "Coles",
                "price": 9.0,
                "unit_price": 1.8,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 9.0,
                "unit_price": 1.8,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 9.8,
                "unit_price": 1.96,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 1650,
            "fat_g": 32.0,
            "saturated_fat_g": 20.0,
            "sugars_g": 0.1,
            "proteins_g": 24.0,
            "salt_g": 1.8
        }
    },
    {
        "id": "chobani_greek_yogurt_170g",
        "name": "Chobani Greek Yogurt 170g",
        "variant": "Blueberry",
        "health_rating": 4.0,
        "stores": [
            {
                "store": "ALDI",
                "price": 1.9,
                "unit_price": 1.12,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 2.5,
                "unit_price": 1.47,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 2.4,
                "unit_price": 1.41,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 2.75,
                "unit_price": 1.62,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 350,
            "fat_g": 0.2,
            "saturated_fat_g": 0.1,
            "sugars_g": 9.0,
            "proteins_g": 9.5,
            "salt_g": 0.1
        }
    },
    {
        "id": "sour_cream_300g",
        "name": "Light Sour Cream 300g",
        "variant": "Reduced Fat",
        "health_rating": 3.5,
        "stores": [
            {
                "store": "ALDI",
                "price": 1.99,
                "unit_price": 0.66,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 2.6,
                "unit_price": 0.87,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 2.55,
                "unit_price": 0.85,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 2.9,
                "unit_price": 0.97,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 700,
            "fat_g": 15.0,
            "saturated_fat_g": 10.0,
            "sugars_g": 3.5,
            "proteins_g": 3.0,
            "salt_g": 0.1
        }
    },
    {
        "id": "almond_milk_1l",
        "name": "Organic Almond Milk 1L",
        "variant": "Unsweetened",
        "health_rating": 4.5,
        "stores": [
            {
                "store": "ALDI",
                "price": 2.2,
                "unit_price": 0.22,
                "unit": "100ml"
            },
            {
                "store": "Coles",
                "price": 2.8,
                "unit_price": 0.28,
                "unit": "100ml"
            },
            {
                "store": "Woolworths",
                "price": 2.75,
                "unit_price": 0.28,
                "unit": "100ml"
            },
            {
                "store": "IGA",
                "price": 3.1,
                "unit_price": 0.31,
                "unit": "100ml"
            }
        ],
        "nutriments": {
            "energy_kj": 70,
            "fat_g": 1.2,
            "saturated_fat_g": 0.1,
            "sugars_g": 0.1,
            "proteins_g": 0.5,
            "salt_g": 0.1
        }
    },
    {
        "id": "almond_milk_vanilla",
        "name": "Organic Almond Milk 1L",
        "variant": "Vanilla Flavor",
        "health_rating": 3.5,
        "stores": [
            {
                "store": "Woolworths",
                "price": 3.0,
                "unit_price": 0.3,
                "unit": "100ml"
            },
            {
                "store": "Coles",
                "price": 3.2,
                "unit_price": 0.32,
                "unit": "100ml"
            }
        ],
        "nutriments": {
            "energy_kj": 120,
            "fat_g": 1.1,
            "saturated_fat_g": 0.1,
            "sugars_g": 3.5,
            "proteins_g": 0.5,
            "salt_g": 0.12
        }
    },
    {
        "id": "oat_milk_barista_1l",
        "name": "Oatly Barista Edition Oat Milk 1L",
        "variant": "Barista",
        "health_rating": 3.5,
        "stores": [
            {
                "store": "ALDI",
                "price": 4.2,
                "unit_price": 0.42,
                "unit": "100ml"
            },
            {
                "store": "Coles",
                "price": 5.5,
                "unit_price": 0.55,
                "unit": "100ml"
            },
            {
                "store": "Woolworths",
                "price": 5.25,
                "unit_price": 0.53,
                "unit": "100ml"
            },
            {
                "store": "IGA",
                "price": 5.8,
                "unit_price": 0.58,
                "unit": "100ml"
            }
        ],
        "nutriments": {
            "energy_kj": 240,
            "fat_g": 3.0,
            "saturated_fat_g": 0.3,
            "sugars_g": 3.2,
            "proteins_g": 1.0,
            "salt_g": 0.1
        }
    },
    {
        "id": "so_good_soy_milk_1l",
        "name": "Sanitarium So Good Soy Milk 1L",
        "variant": "Regular Long Life",
        "health_rating": 4.5,
        "stores": [
            {
                "store": "ALDI",
                "price": 1.9,
                "unit_price": 0.19,
                "unit": "100ml"
            },
            {
                "store": "Coles",
                "price": 2.4,
                "unit_price": 0.24,
                "unit": "100ml"
            },
            {
                "store": "Woolworths",
                "price": 2.4,
                "unit_price": 0.24,
                "unit": "100ml"
            },
            {
                "store": "IGA",
                "price": 2.7,
                "unit_price": 0.27,
                "unit": "100ml"
            }
        ],
        "nutriments": {
            "energy_kj": 240,
            "fat_g": 3.0,
            "saturated_fat_g": 0.4,
            "sugars_g": 2.0,
            "proteins_g": 3.1,
            "salt_g": 0.15
        }
    },
    {
        "id": "vitasoy_rice_milk_1l",
        "name": "Vitasoy Rice Milk Unsweetened 1L",
        "variant": "Calcium Enriched",
        "health_rating": 3.5,
        "stores": [
            {
                "store": "Coles",
                "price": 3.3,
                "unit_price": 0.33,
                "unit": "100ml"
            },
            {
                "store": "Woolworths",
                "price": 3.3,
                "unit_price": 0.33,
                "unit": "100ml"
            },
            {
                "store": "IGA",
                "price": 3.75,
                "unit_price": 0.38,
                "unit": "100ml"
            }
        ],
        "nutriments": {
            "energy_kj": 210,
            "fat_g": 1.0,
            "saturated_fat_g": 0.1,
            "sugars_g": 5.0,
            "proteins_g": 0.3,
            "salt_g": 0.1
        }
    },
    {
        "id": "macadamia_milk_1l",
        "name": "MilkLab Macadamia Milk 1L",
        "variant": "Barista Edition",
        "health_rating": 3.5,
        "stores": [
            {
                "store": "Coles",
                "price": 5.2,
                "unit_price": 0.52,
                "unit": "100ml"
            },
            {
                "store": "Woolworths",
                "price": 5.0,
                "unit_price": 0.5,
                "unit": "100ml"
            },
            {
                "store": "IGA",
                "price": 5.6,
                "unit_price": 0.56,
                "unit": "100ml"
            }
        ],
        "nutriments": {
            "energy_kj": 140,
            "fat_g": 3.5,
            "saturated_fat_g": 0.5,
            "sugars_g": 1.0,
            "proteins_g": 0.5,
            "salt_g": 0.1
        }
    },
    {
        "id": "sourdough_bread_850g",
        "name": "Artisan Sourdough Loaf 850g",
        "variant": "White Sourdough",
        "health_rating": 3.5,
        "stores": [
            {
                "store": "Woolworths",
                "price": 6.5,
                "unit_price": 0.76,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 6.5,
                "unit_price": 0.76,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 7.2,
                "unit_price": 0.85,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 1050,
            "fat_g": 1.2,
            "saturated_fat_g": 0.2,
            "sugars_g": 1.5,
            "proteins_g": 9.5,
            "salt_g": 1.1
        }
    },
    {
        "id": "white_bread_700g",
        "name": "Wonder White Sandwich Bread 700g",
        "variant": "Sliced",
        "health_rating": 2.5,
        "stores": [
            {
                "store": "ALDI",
                "price": 2.7,
                "unit_price": 0.39,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 3.9,
                "unit_price": 0.56,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 3.9,
                "unit_price": 0.56,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 4.2,
                "unit_price": 0.6,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 1000,
            "fat_g": 1.5,
            "saturated_fat_g": 0.3,
            "sugars_g": 2.5,
            "proteins_g": 8.0,
            "salt_g": 1.0
        }
    },
    {
        "id": "wholemeal_bread_700g",
        "name": "Helga's Wholemeal Bread 700g",
        "variant": "Traditional Wholemeal",
        "health_rating": 4.0,
        "stores": [
            {
                "store": "ALDI",
                "price": 3.2,
                "unit_price": 0.46,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 4.4,
                "unit_price": 0.63,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 4.4,
                "unit_price": 0.63,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 4.8,
                "unit_price": 0.69,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 980,
            "fat_g": 2.5,
            "saturated_fat_g": 0.5,
            "sugars_g": 2.5,
            "proteins_g": 9.5,
            "salt_g": 0.9
        }
    },
    {
        "id": "english_muffins_6pk",
        "name": "Tip Top English Muffins 6 Pack",
        "variant": "Original",
        "health_rating": 3.5,
        "stores": [
            {
                "store": "ALDI",
                "price": 2.5,
                "unit_price": 0.42,
                "unit": "ea"
            },
            {
                "store": "Coles",
                "price": 3.5,
                "unit_price": 0.58,
                "unit": "ea"
            },
            {
                "store": "Woolworths",
                "price": 3.5,
                "unit_price": 0.58,
                "unit": "ea"
            },
            {
                "store": "IGA",
                "price": 3.9,
                "unit_price": 0.65,
                "unit": "ea"
            }
        ],
        "nutriments": {
            "energy_kj": 950,
            "fat_g": 1.0,
            "saturated_fat_g": 0.2,
            "sugars_g": 2.0,
            "proteins_g": 8.5,
            "salt_g": 1.2
        }
    },
    {
        "id": "croissants_4pk",
        "name": "All Butter Croissants 4 Pack",
        "variant": "Bakery Fresh",
        "health_rating": 1.5,
        "stores": [
            {
                "store": "ALDI",
                "price": 3.49,
                "unit_price": 0.87,
                "unit": "ea"
            },
            {
                "store": "Coles",
                "price": 4.5,
                "unit_price": 1.13,
                "unit": "ea"
            },
            {
                "store": "Woolworths",
                "price": 4.5,
                "unit_price": 1.13,
                "unit": "ea"
            },
            {
                "store": "IGA",
                "price": 4.9,
                "unit_price": 1.23,
                "unit": "ea"
            }
        ],
        "nutriments": {
            "energy_kj": 1700,
            "fat_g": 21.0,
            "saturated_fat_g": 14.0,
            "sugars_g": 5.0,
            "proteins_g": 7.0,
            "salt_g": 1.0
        }
    },
    {
        "id": "my_muscle_chef_butter_chicken",
        "name": "My Muscle Chef Butter Chicken with Basmati Rice 350g",
        "variant": "High Protein Chilled Meal",
        "health_rating": 4.0,
        "stores": [
            {
                "store": "Coles",
                "price": 10.5,
                "unit_price": 3.0,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 10.5,
                "unit_price": 3.0,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 11.2,
                "unit_price": 3.2,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 550,
            "fat_g": 4.5,
            "saturated_fat_g": 1.5,
            "sugars_g": 2.5,
            "proteins_g": 12.0,
            "salt_g": 0.6
        }
    },
    {
        "id": "woolworths_butter_chicken_350g",
        "name": "Woolworths Indian Butter Chicken 350g",
        "variant": "Chilled Meal",
        "health_rating": 3.5,
        "stores": [
            {
                "store": "Woolworths",
                "price": 8.0,
                "unit_price": 2.29,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 650,
            "fat_g": 7.5,
            "saturated_fat_g": 3.5,
            "sugars_g": 3.5,
            "proteins_g": 8.0,
            "salt_g": 0.8
        }
    },
    {
        "id": "coles_spaghetti_bolognese_350g",
        "name": "Coles Kitchen Spaghetti Bolognese 350g",
        "variant": "Chilled Meal",
        "health_rating": 3.5,
        "stores": [
            {
                "store": "Coles",
                "price": 7.5,
                "unit_price": 2.14,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 520,
            "fat_g": 3.5,
            "saturated_fat_g": 1.2,
            "sugars_g": 2.8,
            "proteins_g": 6.5,
            "salt_g": 0.7
        }
    },
    {
        "id": "youfoodz_chicken_teriyaki_330g",
        "name": "Youfoodz Teriyaki Chicken Bowl 330g",
        "variant": "Fresh Meal",
        "health_rating": 4.0,
        "stores": [
            {
                "store": "Coles",
                "price": 9.95,
                "unit_price": 3.02,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 9.95,
                "unit_price": 3.02,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 10.5,
                "unit_price": 3.18,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 480,
            "fat_g": 2.5,
            "saturated_fat_g": 0.5,
            "sugars_g": 4.5,
            "proteins_g": 10.0,
            "salt_g": 0.65
        }
    },
    {
        "id": "lean_cuisine_lasagne_375g",
        "name": "Lean Cuisine Beef Lasagne 375g",
        "variant": "Frozen Meal",
        "health_rating": 3.5,
        "stores": [
            {
                "store": "ALDI",
                "price": 4.5,
                "unit_price": 1.2,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 6.7,
                "unit_price": 1.79,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 6.5,
                "unit_price": 1.73,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 7.1,
                "unit_price": 1.89,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 450,
            "fat_g": 2.8,
            "saturated_fat_g": 1.2,
            "sugars_g": 3.5,
            "proteins_g": 6.0,
            "salt_g": 0.6
        }
    },
    {
        "id": "mccain_pizza_supreme_500g",
        "name": "McCain Slice Is Right Supreme Pizza 500g",
        "variant": "Frozen Pizza",
        "health_rating": 2.0,
        "stores": [
            {
                "store": "ALDI",
                "price": 5.5,
                "unit_price": 1.1,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 7.5,
                "unit_price": 1.5,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 7.5,
                "unit_price": 1.5,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 8.0,
                "unit_price": 1.6,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 950,
            "fat_g": 8.0,
            "saturated_fat_g": 3.5,
            "sugars_g": 3.0,
            "proteins_g": 9.5,
            "salt_g": 1.2
        }
    },
    {
        "id": "fairtrade_coffee_250g",
        "name": "Fairtrade Organic Coffee Beans 250g",
        "variant": "Medium Roast",
        "health_rating": 5.0,
        "stores": [
            {
                "store": "ALDI",
                "price": 6.5,
                "unit_price": 2.6,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 8.5,
                "unit_price": 3.4,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 8.0,
                "unit_price": 3.2,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 9.2,
                "unit_price": 3.68,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 5,
            "fat_g": 0.0,
            "saturated_fat_g": 0.0,
            "sugars_g": 0.0,
            "proteins_g": 0.1,
            "salt_g": 0.0
        }
    },
    {
        "id": "whole_wheat_flour_1kg",
        "name": "Regenerative Whole Wheat Flour 1kg",
        "variant": "Stoneground Wholemeal",
        "health_rating": 4.0,
        "stores": [
            {
                "store": "Coles",
                "price": 3.5,
                "unit_price": 0.35,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 3.4,
                "unit_price": 0.34,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 3.9,
                "unit_price": 0.39,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 1400,
            "fat_g": 2.0,
            "saturated_fat_g": 0.3,
            "sugars_g": 0.4,
            "proteins_g": 13.0,
            "salt_g": 0.01
        }
    },
    {
        "id": "extra_virgin_olive_oil_1l",
        "name": "Australian Extra Virgin Olive Oil 1L",
        "variant": "Cold Pressed",
        "health_rating": 4.0,
        "stores": [
            {
                "store": "ALDI",
                "price": 14.5,
                "unit_price": 1.45,
                "unit": "100ml"
            },
            {
                "store": "Coles",
                "price": 17.0,
                "unit_price": 1.7,
                "unit": "100ml"
            },
            {
                "store": "Woolworths",
                "price": 16.5,
                "unit_price": 1.65,
                "unit": "100ml"
            },
            {
                "store": "IGA",
                "price": 18.9,
                "unit_price": 1.89,
                "unit": "100ml"
            }
        ],
        "nutriments": {
            "energy_kj": 3400,
            "fat_g": 92.0,
            "saturated_fat_g": 14.0,
            "sugars_g": 0.0,
            "proteins_g": 0.0,
            "salt_g": 0.0
        }
    },
    {
        "id": "basmati_rice_1kg",
        "name": "SunWhite Basmati Rice 1kg",
        "variant": "Long Grain",
        "health_rating": 4.0,
        "stores": [
            {
                "store": "ALDI",
                "price": 3.2,
                "unit_price": 0.32,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 4.5,
                "unit_price": 0.45,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 4.4,
                "unit_price": 0.44,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 4.9,
                "unit_price": 0.49,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 1500,
            "fat_g": 0.6,
            "saturated_fat_g": 0.1,
            "sugars_g": 0.1,
            "proteins_g": 8.0,
            "salt_g": 0.0
        }
    },
    {
        "id": "penne_pasta_500g",
        "name": "Barilla Penne Rigate Pasta 500g",
        "variant": "Semolina Wheat",
        "health_rating": 4.0,
        "stores": [
            {
                "store": "ALDI",
                "price": 1.95,
                "unit_price": 0.39,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 2.9,
                "unit_price": 0.58,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 2.85,
                "unit_price": 0.57,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 3.2,
                "unit_price": 0.64,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 1500,
            "fat_g": 1.5,
            "saturated_fat_g": 0.3,
            "sugars_g": 3.0,
            "proteins_g": 12.0,
            "salt_g": 0.01
        }
    },
    {
        "id": "diced_tomatoes_400g",
        "name": "Organic Diced Tomatoes 400g",
        "variant": "In Juice",
        "health_rating": 5.0,
        "stores": [
            {
                "store": "ALDI",
                "price": 1.1,
                "unit_price": 0.28,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 1.6,
                "unit_price": 0.4,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 1.5,
                "unit_price": 0.38,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 1.8,
                "unit_price": 0.45,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 95,
            "fat_g": 0.1,
            "saturated_fat_g": 0.0,
            "sugars_g": 3.0,
            "proteins_g": 1.0,
            "salt_g": 0.1
        }
    },
    {
        "id": "coconut_milk_400ml",
        "name": "Ayam Coconut Milk 400ml",
        "variant": "Full Fat Premium",
        "health_rating": 3.0,
        "stores": [
            {
                "store": "ALDI",
                "price": 2.1,
                "unit_price": 0.53,
                "unit": "100ml"
            },
            {
                "store": "Coles",
                "price": 3.2,
                "unit_price": 0.8,
                "unit": "100ml"
            },
            {
                "store": "Woolworths",
                "price": 3.1,
                "unit_price": 0.78,
                "unit": "100ml"
            },
            {
                "store": "IGA",
                "price": 3.5,
                "unit_price": 0.88,
                "unit": "100ml"
            }
        ],
        "nutriments": {
            "energy_kj": 750,
            "fat_g": 18.0,
            "saturated_fat_g": 16.0,
            "sugars_g": 1.5,
            "proteins_g": 1.8,
            "salt_g": 0.05
        }
    },
    {
        "id": "soy_sauce_150ml",
        "name": "Kikkoman Soy Sauce 150ml",
        "variant": "Naturally Brewed",
        "health_rating": 2.5,
        "stores": [
            {
                "store": "ALDI",
                "price": 2.8,
                "unit_price": 1.87,
                "unit": "100ml"
            },
            {
                "store": "Coles",
                "price": 3.8,
                "unit_price": 2.53,
                "unit": "100ml"
            },
            {
                "store": "Woolworths",
                "price": 3.8,
                "unit_price": 2.53,
                "unit": "100ml"
            },
            {
                "store": "IGA",
                "price": 4.1,
                "unit_price": 2.73,
                "unit": "100ml"
            }
        ],
        "nutriments": {
            "energy_kj": 250,
            "fat_g": 0.0,
            "saturated_fat_g": 0.0,
            "sugars_g": 1.5,
            "proteins_g": 8.0,
            "salt_g": 16.0
        }
    },
    {
        "id": "white_sugar_1kg",
        "name": "CSR Pure Cane White Sugar 1kg",
        "variant": "Granulated",
        "health_rating": 1.0,
        "stores": [
            {
                "store": "ALDI",
                "price": 1.8,
                "unit_price": 0.18,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 2.5,
                "unit_price": 0.25,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 2.4,
                "unit_price": 0.24,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 2.7,
                "unit_price": 0.27,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 1700,
            "fat_g": 0.0,
            "saturated_fat_g": 0.0,
            "sugars_g": 100.0,
            "proteins_g": 0.0,
            "salt_g": 0.0
        }
    },
    {
        "id": "vegemite_380g",
        "name": "Vegemite Yeast Extract 380g",
        "variant": "Original",
        "health_rating": 4.0,
        "stores": [
            {
                "store": "Coles",
                "price": 5.5,
                "unit_price": 1.45,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 5.4,
                "unit_price": 1.42,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 6.1,
                "unit_price": 1.61,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 750,
            "fat_g": 0.9,
            "saturated_fat_g": 0.1,
            "sugars_g": 2.2,
            "proteins_g": 25.0,
            "salt_g": 8.3
        }
    },
    {
        "id": "peanut_butter_375g",
        "name": "Crunchy Peanut Butter 375g",
        "variant": "No Added Sugar",
        "health_rating": 4.5,
        "stores": [
            {
                "store": "ALDI",
                "price": 3.1,
                "unit_price": 0.83,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 4.0,
                "unit_price": 1.07,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 3.9,
                "unit_price": 1.04,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 2500,
            "fat_g": 50.0,
            "saturated_fat_g": 8.0,
            "sugars_g": 4.5,
            "proteins_g": 25.0,
            "salt_g": 0.8
        }
    },
    {
        "id": "nutella_400g",
        "name": "Nutella Hazelnut Spread 400g",
        "variant": "Original Cocoa Hazelnut",
        "health_rating": 1.0,
        "stores": [
            {
                "store": "ALDI",
                "price": 4.9,
                "unit_price": 1.23,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 6.0,
                "unit_price": 1.5,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 5.9,
                "unit_price": 1.48,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 6.5,
                "unit_price": 1.63,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 2250,
            "fat_g": 30.9,
            "saturated_fat_g": 10.6,
            "sugars_g": 56.3,
            "proteins_g": 5.4,
            "salt_g": 0.1
        }
    },
    {
        "id": "strawberry_jam_500g",
        "name": "IXL Strawberry Jam 500g",
        "variant": "Spread",
        "health_rating": 2.0,
        "stores": [
            {
                "store": "ALDI",
                "price": 2.8,
                "unit_price": 0.56,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 3.9,
                "unit_price": 0.78,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 3.8,
                "unit_price": 0.76,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 4.2,
                "unit_price": 0.84,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 1150,
            "fat_g": 0.1,
            "saturated_fat_g": 0.0,
            "sugars_g": 65.0,
            "proteins_g": 0.3,
            "salt_g": 0.02
        }
    },
    {
        "id": "tomato_sauce_500ml",
        "name": "MasterFoods Tomato Sauce 500ml",
        "variant": "Squeeze Bottle",
        "health_rating": 2.0,
        "stores": [
            {
                "store": "ALDI",
                "price": 2.1,
                "unit_price": 0.42,
                "unit": "100ml"
            },
            {
                "store": "Coles",
                "price": 3.3,
                "unit_price": 0.66,
                "unit": "100ml"
            },
            {
                "store": "Woolworths",
                "price": 3.2,
                "unit_price": 0.64,
                "unit": "100ml"
            },
            {
                "store": "IGA",
                "price": 3.6,
                "unit_price": 0.72,
                "unit": "100ml"
            }
        ],
        "nutriments": {
            "energy_kj": 450,
            "fat_g": 0.1,
            "saturated_fat_g": 0.0,
            "sugars_g": 23.0,
            "proteins_g": 1.0,
            "salt_g": 2.5
        }
    },
    {
        "id": "mayonnaise_470g",
        "name": "S26 Heinz Whole Egg Mayonnaise 470g",
        "variant": "Creamy Original",
        "health_rating": 2.0,
        "stores": [
            {
                "store": "ALDI",
                "price": 3.99,
                "unit_price": 0.85,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 5.5,
                "unit_price": 1.17,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 5.4,
                "unit_price": 1.15,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 5.9,
                "unit_price": 1.26,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 2800,
            "fat_g": 75.0,
            "saturated_fat_g": 6.5,
            "sugars_g": 2.0,
            "proteins_g": 1.5,
            "salt_g": 1.2
        }
    },
    {
        "id": "sanitarium_weet_bix_1.2kg",
        "name": "Sanitarium Weet-Bix Cereal 1.2kg",
        "variant": "Original Whole Grain",
        "health_rating": 5.0,
        "stores": [
            {
                "store": "ALDI",
                "price": 5.8,
                "unit_price": 0.48,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 7.0,
                "unit_price": 0.58,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 7.0,
                "unit_price": 0.58,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 7.6,
                "unit_price": 0.63,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 1500,
            "fat_g": 1.3,
            "saturated_fat_g": 0.3,
            "sugars_g": 3.3,
            "proteins_g": 12.0,
            "salt_g": 0.27
        }
    },
    {
        "id": "rolled_oats_1kg",
        "name": "Organic Rolled Oats 1kg",
        "variant": "Traditional Unrefined",
        "health_rating": 5.0,
        "stores": [
            {
                "store": "ALDI",
                "price": 2.9,
                "unit_price": 0.29,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 3.6,
                "unit_price": 0.36,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 3.5,
                "unit_price": 0.35,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 4.1,
                "unit_price": 0.41,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 1600,
            "fat_g": 9.0,
            "saturated_fat_g": 1.5,
            "sugars_g": 1.0,
            "proteins_g": 13.5,
            "salt_g": 0.01
        }
    },
    {
        "id": "milo_460g",
        "name": "Nestle Milo Chocolate Malt Drink 460g",
        "variant": "Powder Canister",
        "health_rating": 3.5,
        "stores": [
            {
                "store": "ALDI",
                "price": 6.2,
                "unit_price": 1.35,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 8.0,
                "unit_price": 1.74,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 7.85,
                "unit_price": 1.71,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 8.5,
                "unit_price": 1.85,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 1650,
            "fat_g": 9.5,
            "saturated_fat_g": 4.5,
            "sugars_g": 45.0,
            "proteins_g": 12.0,
            "salt_g": 0.4
        }
    },
    {
        "id": "coco_pops_375g",
        "name": "Kellogg's Coco Pops Cereal 375g",
        "variant": "Chocolate Rice",
        "health_rating": 2.0,
        "stores": [
            {
                "store": "ALDI",
                "price": 4.1,
                "unit_price": 1.09,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 5.5,
                "unit_price": 1.47,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 5.4,
                "unit_price": 1.44,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 5.9,
                "unit_price": 1.57,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 1600,
            "fat_g": 1.5,
            "saturated_fat_g": 0.5,
            "sugars_g": 36.0,
            "proteins_g": 5.5,
            "salt_g": 0.7
        }
    },
    {
        "id": "muesli_toasted_500g",
        "name": "Carman's Classic Fruit & Nut Muesli 500g",
        "variant": "Toasted",
        "health_rating": 4.0,
        "stores": [
            {
                "store": "Coles",
                "price": 6.5,
                "unit_price": 1.3,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 6.5,
                "unit_price": 1.3,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 7.1,
                "unit_price": 1.42,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 1850,
            "fat_g": 18.0,
            "saturated_fat_g": 3.5,
            "sugars_g": 12.0,
            "proteins_g": 10.0,
            "salt_g": 0.05
        }
    },
    {
        "id": "arnotts_shapes_barbecue_175g",
        "name": "Arnott's Shapes Savoury Biscuits 175g",
        "variant": "Barbecue",
        "health_rating": 1.5,
        "stores": [
            {
                "store": "ALDI",
                "price": 2.8,
                "unit_price": 1.6,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 3.5,
                "unit_price": 2.0,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 3.5,
                "unit_price": 2.0,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 3.95,
                "unit_price": 2.26,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 2000,
            "fat_g": 22.0,
            "saturated_fat_g": 10.0,
            "sugars_g": 3.5,
            "proteins_g": 8.0,
            "salt_g": 1.5
        }
    },
    {
        "id": "smiths_crinkle_chips_170g",
        "name": "Smith's Crinkle Cut Potato Chips 170g",
        "variant": "Original Salted",
        "health_rating": 2.0,
        "stores": [
            {
                "store": "ALDI",
                "price": 3.2,
                "unit_price": 1.88,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 4.8,
                "unit_price": 2.82,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 4.75,
                "unit_price": 2.79,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 5.2,
                "unit_price": 3.06,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 2200,
            "fat_g": 33.0,
            "saturated_fat_g": 15.0,
            "sugars_g": 0.5,
            "proteins_g": 7.0,
            "salt_g": 1.3
        }
    },
    {
        "id": "red_rock_deli_sea_salt_165g",
        "name": "Red Rock Deli Potato Chips 165g",
        "variant": "Sea Salt & Balsamic Vinegar",
        "health_rating": 2.0,
        "stores": [
            {
                "store": "Coles",
                "price": 5.5,
                "unit_price": 3.33,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 5.5,
                "unit_price": 3.33,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 6.0,
                "unit_price": 3.64,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 2050,
            "fat_g": 23.0,
            "saturated_fat_g": 2.0,
            "sugars_g": 2.5,
            "proteins_g": 7.5,
            "salt_g": 1.4
        }
    },
    {
        "id": "doritos_cheese_supreme_170g",
        "name": "Doritos Corn Chips 170g",
        "variant": "Cheese Supreme",
        "health_rating": 2.0,
        "stores": [
            {
                "store": "ALDI",
                "price": 3.1,
                "unit_price": 1.82,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 4.5,
                "unit_price": 2.65,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 4.5,
                "unit_price": 2.65,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 4.9,
                "unit_price": 2.88,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 2100,
            "fat_g": 25.0,
            "saturated_fat_g": 11.0,
            "sugars_g": 2.0,
            "proteins_g": 7.5,
            "salt_g": 1.4
        }
    },
    {
        "id": "jitz_crackers_250g",
        "name": "Ritz Savoury Crackers 250g",
        "variant": "Original Crisp",
        "health_rating": 2.0,
        "stores": [
            {
                "store": "ALDI",
                "price": 2.2,
                "unit_price": 0.88,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 3.2,
                "unit_price": 1.28,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 3.1,
                "unit_price": 1.24,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 3.5,
                "unit_price": 1.4,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 2050,
            "fat_g": 24.0,
            "saturated_fat_g": 11.0,
            "sugars_g": 7.0,
            "proteins_g": 6.5,
            "salt_g": 1.6
        }
    },
    {
        "id": "salted_cashews_200g",
        "name": "Roasted & Salted Cashews 200g",
        "variant": "Pouch",
        "health_rating": 4.0,
        "stores": [
            {
                "store": "ALDI",
                "price": 3.99,
                "unit_price": 2.0,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 5.5,
                "unit_price": 2.75,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 5.4,
                "unit_price": 2.7,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 6.0,
                "unit_price": 3.0,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 2500,
            "fat_g": 48.0,
            "saturated_fat_g": 9.0,
            "sugars_g": 5.5,
            "proteins_g": 18.0,
            "salt_g": 0.9
        }
    },
    {
        "id": "tim_tam_200g",
        "name": "Arnott's Tim Tam Biscuits 200g",
        "variant": "Original Chocolate",
        "health_rating": 1.0,
        "stores": [
            {
                "store": "ALDI",
                "price": 3.5,
                "unit_price": 1.75,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 4.5,
                "unit_price": 2.25,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 4.5,
                "unit_price": 2.25,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 4.9,
                "unit_price": 2.45,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 2150,
            "fat_g": 26.0,
            "saturated_fat_g": 15.0,
            "sugars_g": 45.0,
            "proteins_g": 4.5,
            "salt_g": 0.4
        }
    },
    {
        "id": "cadbury_dairy_milk_180g",
        "name": "Cadbury Dairy Milk Chocolate Block 180g",
        "variant": "Milk Chocolate",
        "health_rating": 1.5,
        "stores": [
            {
                "store": "Coles",
                "price": 6.0,
                "unit_price": 3.33,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 6.0,
                "unit_price": 3.33,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 6.5,
                "unit_price": 3.61,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 2250,
            "fat_g": 30.0,
            "saturated_fat_g": 19.0,
            "sugars_g": 56.0,
            "proteins_g": 7.0,
            "salt_g": 0.2
        }
    },
    {
        "id": "allen_snakes_alive_200g",
        "name": "Allen's Lollies Confectionery 200g",
        "variant": "Snakes Alive",
        "health_rating": 1.5,
        "stores": [
            {
                "store": "ALDI",
                "price": 2.7,
                "unit_price": 1.35,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 4.0,
                "unit_price": 2.0,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 4.0,
                "unit_price": 2.0,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 4.4,
                "unit_price": 2.2,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 1450,
            "fat_g": 1.0,
            "saturated_fat_g": 1.0,
            "sugars_g": 45.0,
            "proteins_g": 4.0,
            "salt_g": 0.1
        }
    },
    {
        "id": "lindt_excellence_70_100g",
        "name": "Lindt Excellence Dark Chocolate 100g",
        "variant": "70% Cocoa",
        "health_rating": 2.5,
        "stores": [
            {
                "store": "ALDI",
                "price": 4.5,
                "unit_price": 4.5,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 5.5,
                "unit_price": 5.5,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 5.25,
                "unit_price": 5.25,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 5.95,
                "unit_price": 5.95,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 2450,
            "fat_g": 41.0,
            "saturated_fat_g": 24.0,
            "sugars_g": 29.0,
            "proteins_g": 9.5,
            "salt_g": 0.1
        }
    },
    {
        "id": "m_and_ms_peanut_180g",
        "name": "M&M's Peanut Chocolate Medium Bag 180g",
        "variant": "Peanut Candy",
        "health_rating": 1.5,
        "stores": [
            {
                "store": "ALDI",
                "price": 3.8,
                "unit_price": 2.11,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 5.0,
                "unit_price": 2.78,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 5.0,
                "unit_price": 2.78,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 5.5,
                "unit_price": 3.06,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 2150,
            "fat_g": 25.0,
            "saturated_fat_g": 10.0,
            "sugars_g": 53.0,
            "proteins_g": 9.5,
            "salt_g": 0.15
        }
    },
    {
        "id": "chupa_chups_10pk",
        "name": "Chupa Chups Assorted Lollipops 10 Pack",
        "variant": "Fruit & Cream",
        "health_rating": 1.0,
        "stores": [
            {
                "store": "ALDI",
                "price": 2.9,
                "unit_price": 0.29,
                "unit": "ea"
            },
            {
                "store": "Coles",
                "price": 4.0,
                "unit_price": 0.4,
                "unit": "ea"
            },
            {
                "store": "Woolworths",
                "price": 3.9,
                "unit_price": 0.39,
                "unit": "ea"
            },
            {
                "store": "IGA",
                "price": 4.3,
                "unit_price": 0.43,
                "unit": "ea"
            }
        ],
        "nutriments": {
            "energy_kj": 1650,
            "fat_g": 0.0,
            "saturated_fat_g": 0.0,
            "sugars_g": 78.0,
            "proteins_g": 0.0,
            "salt_g": 0.1
        }
    },
    {
        "id": "coca_cola_1.25l",
        "name": "Coca-Cola Classic Soft Drink 1.25L",
        "variant": "Original",
        "health_rating": 1.0,
        "stores": [
            {
                "store": "ALDI",
                "price": 2.2,
                "unit_price": 0.18,
                "unit": "100ml"
            },
            {
                "store": "Coles",
                "price": 3.6,
                "unit_price": 0.29,
                "unit": "100ml"
            },
            {
                "store": "Woolworths",
                "price": 3.55,
                "unit_price": 0.28,
                "unit": "100ml"
            },
            {
                "store": "IGA",
                "price": 3.9,
                "unit_price": 0.31,
                "unit": "100ml"
            }
        ],
        "nutriments": {
            "energy_kj": 180,
            "fat_g": 0.0,
            "saturated_fat_g": 0.0,
            "sugars_g": 10.6,
            "proteins_g": 0.0,
            "salt_g": 0.0
        }
    },
    {
        "id": "remedy_kombucha_330ml",
        "name": "Remedy Organic Kombucha 330ml",
        "variant": "Raspberry Lemonade",
        "health_rating": 4.5,
        "stores": [
            {
                "store": "Coles",
                "price": 3.75,
                "unit_price": 1.14,
                "unit": "100ml"
            },
            {
                "store": "Woolworths",
                "price": 3.75,
                "unit_price": 1.14,
                "unit": "100ml"
            },
            {
                "store": "IGA",
                "price": 4.1,
                "unit_price": 1.24,
                "unit": "100ml"
            }
        ],
        "nutriments": {
            "energy_kj": 25,
            "fat_g": 0.0,
            "saturated_fat_g": 0.0,
            "sugars_g": 0.0,
            "proteins_g": 0.0,
            "salt_g": 0.0
        }
    },
    {
        "id": "lipton_ice_tea_1.5l",
        "name": "Lipton Ice Tea 1.5L",
        "variant": "Peach",
        "health_rating": 2.5,
        "stores": [
            {
                "store": "ALDI",
                "price": 2.9,
                "unit_price": 0.19,
                "unit": "100ml"
            },
            {
                "store": "Coles",
                "price": 4.2,
                "unit_price": 0.28,
                "unit": "100ml"
            },
            {
                "store": "Woolworths",
                "price": 4.1,
                "unit_price": 0.27,
                "unit": "100ml"
            },
            {
                "store": "IGA",
                "price": 4.5,
                "unit_price": 0.3,
                "unit": "100ml"
            }
        ],
        "nutriments": {
            "energy_kj": 120,
            "fat_g": 0.0,
            "saturated_fat_g": 0.0,
            "sugars_g": 6.5,
            "proteins_g": 0.0,
            "salt_g": 0.02
        }
    },
    {
        "id": "mount_franklin_water_20pk",
        "name": "Mount Franklin Spring Water 20 x 500ml",
        "variant": "Still Water",
        "health_rating": 5.0,
        "stores": [
            {
                "store": "ALDI",
                "price": 8.5,
                "unit_price": 0.09,
                "unit": "100ml"
            },
            {
                "store": "Coles",
                "price": 12.0,
                "unit_price": 0.12,
                "unit": "100ml"
            },
            {
                "store": "Woolworths",
                "price": 11.5,
                "unit_price": 0.12,
                "unit": "100ml"
            },
            {
                "store": "IGA",
                "price": 13.0,
                "unit_price": 0.13,
                "unit": "100ml"
            }
        ],
        "nutriments": {
            "energy_kj": 0,
            "fat_g": 0.0,
            "saturated_fat_g": 0.0,
            "sugars_g": 0.0,
            "proteins_g": 0.0,
            "salt_g": 0.0
        }
    },
    {
        "id": "v8_vegetable_juice_1l",
        "name": "V8 Vegetable Juice Original 1L",
        "variant": "100% Vegetable",
        "health_rating": 4.5,
        "stores": [
            {
                "store": "ALDI",
                "price": 3.2,
                "unit_price": 0.32,
                "unit": "100ml"
            },
            {
                "store": "Coles",
                "price": 4.6,
                "unit_price": 0.46,
                "unit": "100ml"
            },
            {
                "store": "Woolworths",
                "price": 4.5,
                "unit_price": 0.45,
                "unit": "100ml"
            },
            {
                "store": "IGA",
                "price": 4.9,
                "unit_price": 0.49,
                "unit": "100ml"
            }
        ],
        "nutriments": {
            "energy_kj": 100,
            "fat_g": 0.1,
            "saturated_fat_g": 0.0,
            "sugars_g": 4.5,
            "proteins_g": 0.8,
            "salt_g": 0.25
        }
    },
    {
        "id": "frozen_peas_1kg",
        "name": "Birds Eye Garden Peas 1kg",
        "variant": "Snap Frozen",
        "health_rating": 5.0,
        "stores": [
            {
                "store": "ALDI",
                "price": 2.6,
                "unit_price": 0.26,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 4.0,
                "unit_price": 0.4,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 3.9,
                "unit_price": 0.39,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 4.3,
                "unit_price": 0.43,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 300,
            "fat_g": 0.5,
            "saturated_fat_g": 0.1,
            "sugars_g": 4.0,
            "proteins_g": 5.5,
            "salt_g": 0.01
        }
    },
    {
        "id": "connoisseur_vanilla_1l",
        "name": "Connoisseur Gourmet Ice Cream 1L",
        "variant": "Vanilla Bean",
        "health_rating": 1.5,
        "stores": [
            {
                "store": "ALDI",
                "price": 7.5,
                "unit_price": 0.75,
                "unit": "100ml"
            },
            {
                "store": "Coles",
                "price": 12.0,
                "unit_price": 1.2,
                "unit": "100ml"
            },
            {
                "store": "Woolworths",
                "price": 11.5,
                "unit_price": 1.15,
                "unit": "100ml"
            },
            {
                "store": "IGA",
                "price": 12.5,
                "unit_price": 1.25,
                "unit": "100ml"
            }
        ],
        "nutriments": {
            "energy_kj": 1050,
            "fat_g": 16.0,
            "saturated_fat_g": 11.0,
            "sugars_g": 20.0,
            "proteins_g": 3.5,
            "salt_g": 0.15
        }
    },
    {
        "id": "fish_fingers_375g",
        "name": "Birds Eye Fish Fingers 375g",
        "variant": "15 Crumbed Fillets",
        "health_rating": 3.5,
        "stores": [
            {
                "store": "ALDI",
                "price": 4.2,
                "unit_price": 1.12,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 6.0,
                "unit_price": 1.6,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 5.8,
                "unit_price": 1.55,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 6.4,
                "unit_price": 1.71,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 850,
            "fat_g": 8.0,
            "saturated_fat_g": 1.0,
            "sugars_g": 1.0,
            "proteins_g": 12.0,
            "salt_g": 0.8
        }
    },
    {
        "id": "frozen_chips_1kg",
        "name": "McCain Superfries Straight Cut 1kg",
        "variant": "Potato Chips",
        "health_rating": 3.0,
        "stores": [
            {
                "store": "ALDI",
                "price": 3.2,
                "unit_price": 0.32,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 5.0,
                "unit_price": 0.5,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 4.9,
                "unit_price": 0.49,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 5.4,
                "unit_price": 0.54,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 650,
            "fat_g": 4.5,
            "saturated_fat_g": 2.0,
            "sugars_g": 0.5,
            "proteins_g": 2.5,
            "salt_g": 0.1
        }
    },
    {
        "id": "baked_beans_420g",
        "name": "Heinz Baked Beans in Tomato Sauce 420g",
        "variant": "Original",
        "health_rating": 4.5,
        "stores": [
            {
                "store": "ALDI",
                "price": 1.6,
                "unit_price": 0.38,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 2.5,
                "unit_price": 0.6,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 2.4,
                "unit_price": 0.57,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 2.7,
                "unit_price": 0.64,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 320,
            "fat_g": 0.5,
            "saturated_fat_g": 0.1,
            "sugars_g": 4.5,
            "proteins_g": 5.0,
            "salt_g": 0.7
        }
    },
    {
        "id": "tuna_oil_95g",
        "name": "Sirena Tuna in Olive Oil 95g",
        "variant": "Canned Tuna",
        "health_rating": 4.5,
        "stores": [
            {
                "store": "ALDI",
                "price": 2.1,
                "unit_price": 2.21,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 3.0,
                "unit_price": 3.16,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 2.9,
                "unit_price": 3.05,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 3.3,
                "unit_price": 3.47,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 1100,
            "fat_g": 18.0,
            "saturated_fat_g": 3.0,
            "sugars_g": 0.1,
            "proteins_g": 25.0,
            "salt_g": 1.0
        }
    },
    {
        "id": "campbells_chicken_soup_430g",
        "name": "Campbell's Country Lad Chicken Soup 430g",
        "variant": "Condensed Canned",
        "health_rating": 3.5,
        "stores": [
            {
                "store": "ALDI",
                "price": 2.2,
                "unit_price": 0.51,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 3.2,
                "unit_price": 0.74,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 3.1,
                "unit_price": 0.72,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 3.5,
                "unit_price": 0.81,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 200,
            "fat_g": 2.0,
            "saturated_fat_g": 0.5,
            "sugars_g": 1.5,
            "proteins_g": 2.5,
            "salt_g": 0.9
        }
    },
    {
        "id": "spam_classic_340g",
        "name": "Spam Canned Meat 340g",
        "variant": "Classic",
        "health_rating": 1.5,
        "stores": [
            {
                "store": "ALDI",
                "price": 4.1,
                "unit_price": 1.21,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 5.8,
                "unit_price": 1.71,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 5.7,
                "unit_price": 1.68,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 6.2,
                "unit_price": 1.82,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 1300,
            "fat_g": 28.0,
            "saturated_fat_g": 11.0,
            "sugars_g": 1.0,
            "proteins_g": 13.0,
            "salt_g": 2.5
        }
    },
    {
        "id": "sriracha_hot_sauce_435ml",
        "name": "Huy Fong Sriracha Hot Chilli Sauce 435ml",
        "variant": "Original Rooster",
        "health_rating": 3.0,
        "stores": [
            {
                "store": "ALDI",
                "price": 3.9,
                "unit_price": 0.9,
                "unit": "100ml"
            },
            {
                "store": "Coles",
                "price": 5.8,
                "unit_price": 1.33,
                "unit": "100ml"
            },
            {
                "store": "Woolworths",
                "price": 5.6,
                "unit_price": 1.29,
                "unit": "100ml"
            },
            {
                "store": "IGA",
                "price": 6.1,
                "unit_price": 1.4,
                "unit": "100ml"
            }
        ],
        "nutriments": {
            "energy_kj": 350,
            "fat_g": 0.0,
            "saturated_fat_g": 0.0,
            "sugars_g": 16.0,
            "proteins_g": 1.5,
            "salt_g": 3.5
        }
    },
    {
        "id": "old_el_paso_taco_kit_520g",
        "name": "Old El Paso Hard & Soft Taco Kit 520g",
        "variant": "Mild Seasoning",
        "health_rating": 2.5,
        "stores": [
            {
                "store": "ALDI",
                "price": 5.2,
                "unit_price": 1.0,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 8.0,
                "unit_price": 1.54,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 7.8,
                "unit_price": 1.5,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 8.5,
                "unit_price": 1.63,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 1500,
            "fat_g": 12.0,
            "saturated_fat_g": 4.5,
            "sugars_g": 4.0,
            "proteins_g": 7.0,
            "salt_g": 1.8
        }
    },
    {
        "id": "indomie_mi_goreng_5pk",
        "name": "Indomie Instant Noodles Mi Goreng 5 Pack",
        "variant": "Original Fried Noodle",
        "health_rating": 1.5,
        "stores": [
            {
                "store": "ALDI",
                "price": 2.8,
                "unit_price": 0.56,
                "unit": "ea"
            },
            {
                "store": "Coles",
                "price": 3.95,
                "unit_price": 0.79,
                "unit": "ea"
            },
            {
                "store": "Woolworths",
                "price": 3.9,
                "unit_price": 0.78,
                "unit": "ea"
            },
            {
                "store": "IGA",
                "price": 4.2,
                "unit_price": 0.84,
                "unit": "ea"
            }
        ],
        "nutriments": {
            "energy_kj": 2000,
            "fat_g": 21.0,
            "saturated_fat_g": 9.0,
            "sugars_g": 8.0,
            "proteins_g": 10.0,
            "salt_g": 1.9
        }
    },
    {
        "id": "feta_cheese_200g",
        "name": "Greek Style Feta Cheese 200g",
        "variant": "Block in Brine",
        "health_rating": 3.0,
        "stores": [
            {
                "store": "ALDI",
                "price": 2.9,
                "unit_price": 1.45,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 4.2,
                "unit_price": 2.1,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 4.0,
                "unit_price": 2.0,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 4.5,
                "unit_price": 2.25,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 1100,
            "fat_g": 21.0,
            "saturated_fat_g": 14.0,
            "sugars_g": 1.0,
            "proteins_g": 16.0,
            "salt_g": 2.5
        }
    },
    {
        "id": "cottage_cheese_500g",
        "name": "High Protein Cottage Cheese 500g",
        "variant": "Low Fat",
        "health_rating": 4.5,
        "stores": [
            {
                "store": "ALDI",
                "price": 3.2,
                "unit_price": 0.64,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 4.5,
                "unit_price": 0.9,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 4.4,
                "unit_price": 0.88,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 4.8,
                "unit_price": 0.96,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 350,
            "fat_g": 2.5,
            "saturated_fat_g": 1.5,
            "sugars_g": 3.0,
            "proteins_g": 12.0,
            "salt_g": 0.8
        }
    },
    {
        "id": "almond_milk_chocolate_1l",
        "name": "Organic Almond Milk 1L",
        "variant": "Chocolate Flavor",
        "health_rating": 3.0,
        "stores": [
            {
                "store": "Woolworths",
                "price": 3.2,
                "unit_price": 0.32,
                "unit": "100ml"
            },
            {
                "store": "Coles",
                "price": 3.3,
                "unit_price": 0.33,
                "unit": "100ml"
            }
        ],
        "nutriments": {
            "energy_kj": 200,
            "fat_g": 1.5,
            "saturated_fat_g": 0.2,
            "sugars_g": 6.5,
            "proteins_g": 0.6,
            "salt_g": 0.15
        }
    },
    {
        "id": "cashew_milk_1l",
        "name": "So Delicious Cashew Milk 1L",
        "variant": "Unsweetened",
        "health_rating": 4.0,
        "stores": [
            {
                "store": "Coles",
                "price": 4.8,
                "unit_price": 0.48,
                "unit": "100ml"
            },
            {
                "store": "Woolworths",
                "price": 4.75,
                "unit_price": 0.48,
                "unit": "100ml"
            },
            {
                "store": "IGA",
                "price": 5.1,
                "unit_price": 0.51,
                "unit": "100ml"
            }
        ],
        "nutriments": {
            "energy_kj": 100,
            "fat_g": 2.0,
            "saturated_fat_g": 0.4,
            "sugars_g": 0.2,
            "proteins_g": 0.8,
            "salt_g": 0.1
        }
    },
    {
        "id": "red_lentils_1kg",
        "name": "Split Red Lentils 1kg",
        "variant": "Uncooked Dried",
        "health_rating": 5.0,
        "stores": [
            {
                "store": "ALDI",
                "price": 2.2,
                "unit_price": 0.22,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 3.1,
                "unit_price": 0.31,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 3.0,
                "unit_price": 0.3,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 3.4,
                "unit_price": 0.34,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 1450,
            "fat_g": 1.5,
            "saturated_fat_g": 0.2,
            "sugars_g": 2.0,
            "proteins_g": 25.0,
            "salt_g": 0.01
        }
    },
    {
        "id": "chickpeas_canned_400g",
        "name": "Organic Chickpeas 400g",
        "variant": "Canned in Water",
        "health_rating": 5.0,
        "stores": [
            {
                "store": "ALDI",
                "price": 1.0,
                "unit_price": 0.25,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 1.5,
                "unit_price": 0.38,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 1.45,
                "unit_price": 0.36,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 1.7,
                "unit_price": 0.43,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 450,
            "fat_g": 2.5,
            "saturated_fat_g": 0.3,
            "sugars_g": 0.5,
            "proteins_g": 6.5,
            "salt_g": 0.5
        }
    },
    {
        "id": "quinoa_organic_500g",
        "name": "Organic White Quinoa 500g",
        "variant": "Whole Grain",
        "health_rating": 5.0,
        "stores": [
            {
                "store": "ALDI",
                "price": 4.5,
                "unit_price": 0.9,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 6.2,
                "unit_price": 1.24,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 6.0,
                "unit_price": 1.2,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 6.8,
                "unit_price": 1.36,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 1550,
            "fat_g": 6.0,
            "saturated_fat_g": 0.7,
            "sugars_g": 2.0,
            "proteins_g": 14.0,
            "salt_g": 0.01
        }
    },
    {
        "id": "jasmine_rice_2kg",
        "name": "Fragrant Jasmine Rice 2kg",
        "variant": "Long Grain White",
        "health_rating": 4.0,
        "stores": [
            {
                "store": "ALDI",
                "price": 5.8,
                "unit_price": 0.29,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 8.0,
                "unit_price": 0.4,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 7.8,
                "unit_price": 0.39,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 8.6,
                "unit_price": 0.43,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 1500,
            "fat_g": 0.5,
            "saturated_fat_g": 0.1,
            "sugars_g": 0.1,
            "proteins_g": 7.5,
            "salt_g": 0.0
        }
    },
    {
        "id": "sesame_oil_150ml",
        "name": "Pure Sesame Oil 150ml",
        "variant": "Toasted",
        "health_rating": 4.0,
        "stores": [
            {
                "store": "ALDI",
                "price": 3.2,
                "unit_price": 2.13,
                "unit": "100ml"
            },
            {
                "store": "Coles",
                "price": 4.8,
                "unit_price": 3.2,
                "unit": "100ml"
            },
            {
                "store": "Woolworths",
                "price": 4.7,
                "unit_price": 3.13,
                "unit": "100ml"
            },
            {
                "store": "IGA",
                "price": 5.2,
                "unit_price": 3.47,
                "unit": "100ml"
            }
        ],
        "nutriments": {
            "energy_kj": 3400,
            "fat_g": 92.0,
            "saturated_fat_g": 13.0,
            "sugars_g": 0.0,
            "proteins_g": 0.0,
            "salt_g": 0.0
        }
    },
    {
        "id": "balsamic_vinegar_250ml",
        "name": "Balsamic Vinegar of Modena 250ml",
        "variant": "Aged",
        "health_rating": 4.5,
        "stores": [
            {
                "store": "ALDI",
                "price": 3.5,
                "unit_price": 1.4,
                "unit": "100ml"
            },
            {
                "store": "Coles",
                "price": 5.2,
                "unit_price": 2.08,
                "unit": "100ml"
            },
            {
                "store": "Woolworths",
                "price": 5.0,
                "unit_price": 2.0,
                "unit": "100ml"
            },
            {
                "store": "IGA",
                "price": 5.6,
                "unit_price": 2.24,
                "unit": "100ml"
            }
        ],
        "nutriments": {
            "energy_kj": 350,
            "fat_g": 0.0,
            "saturated_fat_g": 0.0,
            "sugars_g": 15.0,
            "proteins_g": 0.5,
            "salt_g": 0.05
        }
    },
    {
        "id": "dijon_mustard_200g",
        "name": "French Dijon Mustard 200g",
        "variant": "Glass Jar",
        "health_rating": 4.0,
        "stores": [
            {
                "store": "ALDI",
                "price": 2.1,
                "unit_price": 1.05,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 3.4,
                "unit_price": 1.7,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 3.3,
                "unit_price": 1.65,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 3.7,
                "unit_price": 1.85,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 650,
            "fat_g": 11.0,
            "saturated_fat_g": 0.8,
            "sugars_g": 2.5,
            "proteins_g": 7.0,
            "salt_g": 5.5
        }
    },
    {
        "id": "carman_protein_bars_5pk",
        "name": "Carman's Protein Bars 5 Pack",
        "variant": "Salted Caramel Nut",
        "health_rating": 3.5,
        "stores": [
            {
                "store": "ALDI",
                "price": 5.2,
                "unit_price": 1.04,
                "unit": "ea"
            },
            {
                "store": "Coles",
                "price": 7.8,
                "unit_price": 1.56,
                "unit": "ea"
            },
            {
                "store": "Woolworths",
                "price": 7.5,
                "unit_price": 1.5,
                "unit": "ea"
            },
            {
                "store": "IGA",
                "price": 8.2,
                "unit_price": 1.64,
                "unit": "ea"
            }
        ],
        "nutriments": {
            "energy_kj": 1800,
            "fat_g": 20.0,
            "saturated_fat_g": 4.5,
            "sugars_g": 14.0,
            "proteins_g": 26.0,
            "salt_g": 0.8
        }
    },
    {
        "id": "uncle_tobys_muesli_bars_6pk",
        "name": "Uncle Tobys Chewy Muesli Bars 6 Pack",
        "variant": "Choc Chip",
        "health_rating": 3.5,
        "stores": [
            {
                "store": "ALDI",
                "price": 3.2,
                "unit_price": 0.53,
                "unit": "ea"
            },
            {
                "store": "Coles",
                "price": 5.0,
                "unit_price": 0.83,
                "unit": "ea"
            },
            {
                "store": "Woolworths",
                "price": 4.8,
                "unit_price": 0.8,
                "unit": "ea"
            },
            {
                "store": "IGA",
                "price": 5.3,
                "unit_price": 0.88,
                "unit": "ea"
            }
        ],
        "nutriments": {
            "energy_kj": 1650,
            "fat_g": 11.0,
            "saturated_fat_g": 3.0,
            "sugars_g": 18.0,
            "proteins_g": 7.5,
            "salt_g": 0.15
        }
    },
    {
        "id": "rice_crackers_100g",
        "name": "Fantastic Rice Crackers 100g",
        "variant": "Original Salted",
        "health_rating": 2.5,
        "stores": [
            {
                "store": "ALDI",
                "price": 1.3,
                "unit_price": 1.3,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 2.2,
                "unit_price": 2.2,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 2.1,
                "unit_price": 2.1,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 2.4,
                "unit_price": 2.4,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 1700,
            "fat_g": 2.5,
            "saturated_fat_g": 1.0,
            "sugars_g": 1.5,
            "proteins_g": 8.0,
            "salt_g": 1.2
        }
    },
    {
        "id": "english_breakfast_tea_100pk",
        "name": "Twinings English Breakfast Tea Bags 100 Pack",
        "variant": "Black Tea",
        "health_rating": 5.0,
        "stores": [
            {
                "store": "ALDI",
                "price": 6.8,
                "unit_price": 0.07,
                "unit": "ea"
            },
            {
                "store": "Coles",
                "price": 11.0,
                "unit_price": 0.11,
                "unit": "ea"
            },
            {
                "store": "Woolworths",
                "price": 10.5,
                "unit_price": 0.11,
                "unit": "ea"
            },
            {
                "store": "IGA",
                "price": 11.8,
                "unit_price": 0.12,
                "unit": "ea"
            }
        ],
        "nutriments": {
            "energy_kj": 5,
            "fat_g": 0.0,
            "saturated_fat_g": 0.0,
            "sugars_g": 0.0,
            "proteins_g": 0.0,
            "salt_g": 0.0
        }
    },
    {
        "id": "green_tea_50pk",
        "name": "Dilmah Pure Green Tea 50 Pack",
        "variant": "Green Tea Bags",
        "health_rating": 5.0,
        "stores": [
            {
                "store": "ALDI",
                "price": 3.9,
                "unit_price": 0.08,
                "unit": "ea"
            },
            {
                "store": "Coles",
                "price": 5.8,
                "unit_price": 0.12,
                "unit": "ea"
            },
            {
                "store": "Woolworths",
                "price": 5.5,
                "unit_price": 0.11,
                "unit": "ea"
            },
            {
                "store": "IGA",
                "price": 6.2,
                "unit_price": 0.12,
                "unit": "ea"
            }
        ],
        "nutriments": {
            "energy_kj": 5,
            "fat_g": 0.0,
            "saturated_fat_g": 0.0,
            "sugars_g": 0.0,
            "proteins_g": 0.0,
            "salt_g": 0.0
        }
    },
    {
        "id": "orange_juice_2l",
        "name": "Daily Juice Orange Juice 2L",
        "variant": "No Added Sugar with Pulp",
        "health_rating": 3.5,
        "stores": [
            {
                "store": "ALDI",
                "price": 4.5,
                "unit_price": 0.23,
                "unit": "100ml"
            },
            {
                "store": "Coles",
                "price": 6.5,
                "unit_price": 0.33,
                "unit": "100ml"
            },
            {
                "store": "Woolworths",
                "price": 6.3,
                "unit_price": 0.32,
                "unit": "100ml"
            },
            {
                "store": "IGA",
                "price": 6.9,
                "unit_price": 0.35,
                "unit": "100ml"
            }
        ],
        "nutriments": {
            "energy_kj": 180,
            "fat_g": 0.1,
            "saturated_fat_g": 0.0,
            "sugars_g": 9.5,
            "proteins_g": 0.7,
            "salt_g": 0.01
        }
    },
    {
        "id": "sparkling_water_1.25l",
        "name": "San Pellegrino Sparkling Mineral Water 1.25L",
        "variant": "Bottled Mineral Water",
        "health_rating": 5.0,
        "stores": [
            {
                "store": "ALDI",
                "price": 2.2,
                "unit_price": 0.18,
                "unit": "100ml"
            },
            {
                "store": "Coles",
                "price": 3.4,
                "unit_price": 0.27,
                "unit": "100ml"
            },
            {
                "store": "Woolworths",
                "price": 3.3,
                "unit_price": 0.26,
                "unit": "100ml"
            },
            {
                "store": "IGA",
                "price": 3.7,
                "unit_price": 0.3,
                "unit": "100ml"
            }
        ],
        "nutriments": {
            "energy_kj": 0,
            "fat_g": 0.0,
            "saturated_fat_g": 0.0,
            "sugars_g": 0.0,
            "proteins_g": 0.0,
            "salt_g": 0.0
        }
    },
    {
        "id": "magnum_classic_4pk",
        "name": "Streets Magnum Ice Cream Stick 4 Pack",
        "variant": "Classic Vanilla Chocolate",
        "health_rating": 1.5,
        "stores": [
            {
                "store": "ALDI",
                "price": 6.5,
                "unit_price": 1.63,
                "unit": "ea"
            },
            {
                "store": "Coles",
                "price": 10.5,
                "unit_price": 2.63,
                "unit": "ea"
            },
            {
                "store": "Woolworths",
                "price": 10.0,
                "unit_price": 2.5,
                "unit": "ea"
            },
            {
                "store": "IGA",
                "price": 11.0,
                "unit_price": 2.75,
                "unit": "ea"
            }
        ],
        "nutriments": {
            "energy_kj": 1300,
            "fat_g": 20.0,
            "saturated_fat_g": 14.0,
            "sugars_g": 26.0,
            "proteins_g": 3.5,
            "salt_g": 0.15
        }
    },
    {
        "id": "weis_bars_4pk",
        "name": "Weis Mango & Cream Bars 4 Pack",
        "variant": "Real Fruit Ice Bars",
        "health_rating": 2.5,
        "stores": [
            {
                "store": "ALDI",
                "price": 5.2,
                "unit_price": 1.3,
                "unit": "ea"
            },
            {
                "store": "Coles",
                "price": 8.0,
                "unit_price": 2.0,
                "unit": "ea"
            },
            {
                "store": "Woolworths",
                "price": 7.8,
                "unit_price": 1.95,
                "unit": "ea"
            },
            {
                "store": "IGA",
                "price": 8.5,
                "unit_price": 2.13,
                "unit": "ea"
            }
        ],
        "nutriments": {
            "energy_kj": 750,
            "fat_g": 8.0,
            "saturated_fat_g": 5.0,
            "sugars_g": 21.0,
            "proteins_g": 1.5,
            "salt_g": 0.05
        }
    },
    {
        "id": "chicken_thigh_500g",
        "name": "Chicken Thigh Fillets 500g",
        "variant": "Skinless Boneless",
        "health_rating": 4.5,
        "stores": [
            {
                "store": "ALDI",
                "price": 6.8,
                "unit_price": 1.36,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 8.0,
                "unit_price": 1.6,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 7.8,
                "unit_price": 1.56,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 8.5,
                "unit_price": 1.7,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 670,
            "fat_g": 8.0,
            "saturated_fat_g": 2.2,
            "sugars_g": 0.0,
            "proteins_g": 19.5,
            "salt_g": 0.14
        }
    },
    {
        "id": "beef_rump_steak_500g",
        "name": "Grass-Fed Beef Rump Steak 500g",
        "variant": "Boneless Cut",
        "health_rating": 4.5,
        "stores": [
            {
                "store": "ALDI",
                "price": 12.5,
                "unit_price": 2.5,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 15.0,
                "unit_price": 3.0,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 14.8,
                "unit_price": 2.96,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 16.0,
                "unit_price": 3.2,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 550,
            "fat_g": 4.0,
            "saturated_fat_g": 1.8,
            "sugars_g": 0.0,
            "proteins_g": 22.0,
            "salt_g": 0.13
        }
    },
    {
        "id": "sliced_ham_200g",
        "name": "Primo Double Smoked Leg Ham 200g",
        "variant": "Deli Sliced",
        "health_rating": 2.5,
        "stores": [
            {
                "store": "ALDI",
                "price": 3.8,
                "unit_price": 1.9,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 5.5,
                "unit_price": 2.75,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 5.2,
                "unit_price": 2.6,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 5.8,
                "unit_price": 2.9,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 450,
            "fat_g": 3.5,
            "saturated_fat_g": 1.2,
            "sugars_g": 1.5,
            "proteins_g": 16.0,
            "salt_g": 2.2
        }
    },
    {
        "id": "hummus_dip_200g",
        "name": "Obela Hommus Classic Dip 200g",
        "variant": "Original Chickpea Dip",
        "health_rating": 4.5,
        "stores": [
            {
                "store": "ALDI",
                "price": 2.5,
                "unit_price": 1.25,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 4.0,
                "unit_price": 2.0,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 3.9,
                "unit_price": 1.95,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 4.3,
                "unit_price": 2.15,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 1150,
            "fat_g": 22.0,
            "saturated_fat_g": 2.5,
            "sugars_g": 1.0,
            "proteins_g": 7.5,
            "salt_g": 1.1
        }
    },
    {
        "id": "popcorn_salted_100g",
        "name": "Cobs Popcorn Lightly Salted 100g",
        "variant": "Air Popped",
        "health_rating": 4.0,
        "stores": [
            {
                "store": "ALDI",
                "price": 2.2,
                "unit_price": 2.2,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 3.5,
                "unit_price": 3.5,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 3.4,
                "unit_price": 3.4,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 3.8,
                "unit_price": 3.8,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 1950,
            "fat_g": 22.0,
            "saturated_fat_g": 2.0,
            "sugars_g": 0.5,
            "proteins_g": 9.0,
            "salt_g": 1.1
        }
    },
    {
        "id": "pringles_original_134g",
        "name": "Pringles Potato Chips 134g",
        "variant": "Original Salted Canister",
        "health_rating": 1.5,
        "stores": [
            {
                "store": "ALDI",
                "price": 3.2,
                "unit_price": 2.39,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 5.0,
                "unit_price": 3.73,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 4.8,
                "unit_price": 3.58,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 5.3,
                "unit_price": 3.96,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 2150,
            "fat_g": 33.0,
            "saturated_fat_g": 15.0,
            "sugars_g": 0.5,
            "proteins_g": 4.0,
            "salt_g": 1.3
        }
    },
    {
        "id": "twix_bar_50g",
        "name": "Twix Caramel Biscuit Chocolate Bar 50g",
        "variant": "Single Bar",
        "health_rating": 1.0,
        "stores": [
            {
                "store": "ALDI",
                "price": 1.2,
                "unit_price": 2.4,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 2.2,
                "unit_price": 4.4,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 2.1,
                "unit_price": 4.2,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 2.4,
                "unit_price": 4.8,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 2050,
            "fat_g": 24.0,
            "saturated_fat_g": 14.0,
            "sugars_g": 49.0,
            "proteins_g": 4.5,
            "salt_g": 0.4
        }
    },
    {
        "id": "kitkat_4finger_45g",
        "name": "Nestle KitKat Milk Chocolate Bar 45g",
        "variant": "4 Finger",
        "health_rating": 1.0,
        "stores": [
            {
                "store": "ALDI",
                "price": 1.2,
                "unit_price": 2.67,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 2.2,
                "unit_price": 4.89,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 2.0,
                "unit_price": 4.44,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 2.3,
                "unit_price": 5.11,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 2100,
            "fat_g": 25.0,
            "saturated_fat_g": 14.0,
            "sugars_g": 49.0,
            "proteins_g": 6.5,
            "salt_g": 0.2
        }
    },
    {
        "id": "pepsi_max_1.25l",
        "name": "Pepsi Max No Sugar Soft Drink 1.25L",
        "variant": "Zero Sugar Cola",
        "health_rating": 2.5,
        "stores": [
            {
                "store": "ALDI",
                "price": 1.9,
                "unit_price": 0.15,
                "unit": "100ml"
            },
            {
                "store": "Coles",
                "price": 3.2,
                "unit_price": 0.26,
                "unit": "100ml"
            },
            {
                "store": "Woolworths",
                "price": 3.1,
                "unit_price": 0.25,
                "unit": "100ml"
            },
            {
                "store": "IGA",
                "price": 3.5,
                "unit_price": 0.28,
                "unit": "100ml"
            }
        ],
        "nutriments": {
            "energy_kj": 2,
            "fat_g": 0.0,
            "saturated_fat_g": 0.0,
            "sugars_g": 0.0,
            "proteins_g": 0.0,
            "salt_g": 0.02
        }
    },
    {
        "id": "fanta_orange_1.25l",
        "name": "Fanta Orange Soft Drink 1.25L",
        "variant": "Orange Flavor",
        "health_rating": 1.0,
        "stores": [
            {
                "store": "ALDI",
                "price": 2.1,
                "unit_price": 0.17,
                "unit": "100ml"
            },
            {
                "store": "Coles",
                "price": 3.5,
                "unit_price": 0.28,
                "unit": "100ml"
            },
            {
                "store": "Woolworths",
                "price": 3.4,
                "unit_price": 0.27,
                "unit": "100ml"
            },
            {
                "store": "IGA",
                "price": 3.8,
                "unit_price": 0.3,
                "unit": "100ml"
            }
        ],
        "nutriments": {
            "energy_kj": 190,
            "fat_g": 0.0,
            "saturated_fat_g": 0.0,
            "sugars_g": 11.0,
            "proteins_g": 0.0,
            "salt_g": 0.02
        }
    },
    {
        "id": "red_bull_250ml",
        "name": "Red Bull Energy Drink 250ml",
        "variant": "Original",
        "health_rating": 1.5,
        "stores": [
            {
                "store": "ALDI",
                "price": 2.5,
                "unit_price": 1.0,
                "unit": "100ml"
            },
            {
                "store": "Coles",
                "price": 3.8,
                "unit_price": 1.52,
                "unit": "100ml"
            },
            {
                "store": "Woolworths",
                "price": 3.7,
                "unit_price": 1.48,
                "unit": "100ml"
            },
            {
                "store": "IGA",
                "price": 4.1,
                "unit_price": 1.64,
                "unit": "100ml"
            }
        ],
        "nutriments": {
            "energy_kj": 195,
            "fat_g": 0.0,
            "saturated_fat_g": 0.0,
            "sugars_g": 11.0,
            "proteins_g": 0.0,
            "salt_g": 0.1
        }
    },
    {
        "id": "sea_salt_flake_250g",
        "name": "Maldon Sea Salt Flakes 250g",
        "variant": "Box Flakes",
        "health_rating": 2.0,
        "stores": [
            {
                "store": "Coles",
                "price": 7.5,
                "unit_price": 3.0,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 7.3,
                "unit_price": 2.92,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 8.0,
                "unit_price": 3.2,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 0,
            "fat_g": 0.0,
            "saturated_fat_g": 0.0,
            "sugars_g": 0.0,
            "proteins_g": 0.0,
            "salt_g": 100.0
        }
    },
    {
        "id": "black_pepper_grinder_50g",
        "name": "MasterFoods Black Peppercorn Grinder 50g",
        "variant": "Whole Peppercorns",
        "health_rating": 5.0,
        "stores": [
            {
                "store": "ALDI",
                "price": 3.2,
                "unit_price": 6.4,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 5.0,
                "unit_price": 10.0,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 4.9,
                "unit_price": 9.8,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 5.4,
                "unit_price": 10.8,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 1050,
            "fat_g": 3.0,
            "saturated_fat_g": 1.0,
            "sugars_g": 0.5,
            "proteins_g": 10.0,
            "salt_g": 0.05
        }
    },
    {
        "id": "honey_375g",
        "name": "Capilano Pure Australian Honey 375g",
        "variant": "Squeeze Bottle",
        "health_rating": 3.5,
        "stores": [
            {
                "store": "ALDI",
                "price": 5.2,
                "unit_price": 1.39,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 7.5,
                "unit_price": 2.0,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 7.2,
                "unit_price": 1.92,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 8.0,
                "unit_price": 2.13,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 1400,
            "fat_g": 0.0,
            "saturated_fat_g": 0.0,
            "sugars_g": 82.0,
            "proteins_g": 0.3,
            "salt_g": 0.01
        }
    },
    {
        "id": "maple_syrup_250ml",
        "name": "Pure Canadian Maple Syrup 250ml",
        "variant": "Grade A Dark",
        "health_rating": 2.5,
        "stores": [
            {
                "store": "ALDI",
                "price": 6.5,
                "unit_price": 2.6,
                "unit": "100ml"
            },
            {
                "store": "Coles",
                "price": 9.5,
                "unit_price": 3.8,
                "unit": "100ml"
            },
            {
                "store": "Woolworths",
                "price": 9.2,
                "unit_price": 3.68,
                "unit": "100ml"
            },
            {
                "store": "IGA",
                "price": 10.0,
                "unit_price": 4.0,
                "unit": "100ml"
            }
        ],
        "nutriments": {
            "energy_kj": 1100,
            "fat_g": 0.0,
            "saturated_fat_g": 0.0,
            "sugars_g": 67.0,
            "proteins_g": 0.0,
            "salt_g": 0.03
        }
    },
    {
        "id": "frozen_berries_500g",
        "name": "Mixed Berries 500g",
        "variant": "Frozen Blueberries, Strawberries & Blackberries",
        "health_rating": 5.0,
        "stores": [
            {
                "store": "ALDI",
                "price": 4.5,
                "unit_price": 0.9,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 6.8,
                "unit_price": 1.36,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 6.5,
                "unit_price": 1.3,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 7.2,
                "unit_price": 1.44,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 180,
            "fat_g": 0.5,
            "saturated_fat_g": 0.0,
            "sugars_g": 6.0,
            "proteins_g": 1.2,
            "salt_g": 0.01
        }
    },
    {
        "id": "frozen_mango_500g",
        "name": "Frozen Mango Chunks 500g",
        "variant": "100% Real Fruit",
        "health_rating": 5.0,
        "stores": [
            {
                "store": "ALDI",
                "price": 4.9,
                "unit_price": 0.98,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 7.0,
                "unit_price": 1.4,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 6.8,
                "unit_price": 1.36,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 7.5,
                "unit_price": 1.5,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 250,
            "fat_g": 0.2,
            "saturated_fat_g": 0.0,
            "sugars_g": 13.0,
            "proteins_g": 0.8,
            "salt_g": 0.0
        }
    },
    {
        "id": "sardines_in_oil_110g",
        "name": "Brunswick Sardines in Olive Oil 110g",
        "variant": "Canned Sardines",
        "health_rating": 5.0,
        "stores": [
            {
                "store": "ALDI",
                "price": 1.8,
                "unit_price": 1.64,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 2.8,
                "unit_price": 2.55,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 2.7,
                "unit_price": 2.45,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 3.0,
                "unit_price": 2.73,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 850,
            "fat_g": 12.0,
            "saturated_fat_g": 3.0,
            "sugars_g": 0.0,
            "proteins_g": 24.0,
            "salt_g": 0.8
        }
    },
    {
        "id": "salmon_canned_210g",
        "name": "John West Red Salmon 210g",
        "variant": "Wild Alaskan",
        "health_rating": 5.0,
        "stores": [
            {
                "store": "ALDI",
                "price": 4.5,
                "unit_price": 2.14,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 7.0,
                "unit_price": 3.33,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 6.8,
                "unit_price": 3.24,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 7.5,
                "unit_price": 3.57,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 600,
            "fat_g": 6.5,
            "saturated_fat_g": 1.5,
            "sugars_g": 0.0,
            "proteins_g": 20.0,
            "salt_g": 0.9
        }
    },
    {
        "id": "baking_powder_125g",
        "name": "McKenzie's Baking Powder 125g",
        "variant": "Leavening Agent",
        "health_rating": 4.0,
        "stores": [
            {
                "store": "ALDI",
                "price": 1.5,
                "unit_price": 1.2,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 2.3,
                "unit_price": 1.84,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 2.2,
                "unit_price": 1.76,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 2.5,
                "unit_price": 2.0,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 220,
            "fat_g": 0.0,
            "saturated_fat_g": 0.0,
            "sugars_g": 0.0,
            "proteins_g": 0.1,
            "salt_g": 27.0
        }
    },
    {
        "id": "vanilla_extract_50ml",
        "name": "Queen Pure Vanilla Extract 50ml",
        "variant": "Concentrated Flavoring",
        "health_rating": 4.0,
        "stores": [
            {
                "store": "ALDI",
                "price": 5.2,
                "unit_price": 10.4,
                "unit": "100ml"
            },
            {
                "store": "Coles",
                "price": 8.0,
                "unit_price": 16.0,
                "unit": "100ml"
            },
            {
                "store": "Woolworths",
                "price": 7.8,
                "unit_price": 15.6,
                "unit": "100ml"
            },
            {
                "store": "IGA",
                "price": 8.5,
                "unit_price": 17.0,
                "unit": "100ml"
            }
        ],
        "nutriments": {
            "energy_kj": 1200,
            "fat_g": 0.0,
            "saturated_fat_g": 0.0,
            "sugars_g": 12.0,
            "proteins_g": 0.0,
            "salt_g": 0.0
        }
    },
    {
        "id": "cocoa_powder_175g",
        "name": "Cadbury Cocoa Powder 175g",
        "variant": "Baking Cocoa",
        "health_rating": 4.0,
        "stores": [
            {
                "store": "ALDI",
                "price": 3.8,
                "unit_price": 2.17,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 5.5,
                "unit_price": 3.14,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 5.3,
                "unit_price": 3.03,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 5.9,
                "unit_price": 3.37,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 1400,
            "fat_g": 11.0,
            "saturated_fat_g": 6.5,
            "sugars_g": 0.5,
            "proteins_g": 22.0,
            "salt_g": 0.05
        }
    },
    {
        "id": "cornflour_300g",
        "name": "Fielders Cornflour 300g",
        "variant": "Thickening Agent",
        "health_rating": 3.5,
        "stores": [
            {
                "store": "ALDI",
                "price": 1.8,
                "unit_price": 0.6,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 2.8,
                "unit_price": 0.93,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 2.7,
                "unit_price": 0.9,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 3.0,
                "unit_price": 1.0,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 1500,
            "fat_g": 0.1,
            "saturated_fat_g": 0.0,
            "sugars_g": 0.0,
            "proteins_g": 0.3,
            "salt_g": 0.01
        }
    },
    {
        "id": "apple_cider_vinegar_500ml",
        "name": "Bragg Organic Apple Cider Vinegar 500ml",
        "variant": "With The Mother",
        "health_rating": 5.0,
        "stores": [
            {
                "store": "Coles",
                "price": 8.5,
                "unit_price": 1.7,
                "unit": "100ml"
            },
            {
                "store": "Woolworths",
                "price": 8.3,
                "unit_price": 1.66,
                "unit": "100ml"
            },
            {
                "store": "IGA",
                "price": 9.0,
                "unit_price": 1.8,
                "unit": "100ml"
            }
        ],
        "nutriments": {
            "energy_kj": 90,
            "fat_g": 0.0,
            "saturated_fat_g": 0.0,
            "sugars_g": 0.4,
            "proteins_g": 0.0,
            "salt_g": 0.0
        }
    },
    {
        "id": "almond_butter_250g",
        "name": "Mayver's Pure Almond Spread 250g",
        "variant": "100% Almonds",
        "health_rating": 4.5,
        "stores": [
            {
                "store": "ALDI",
                "price": 5.5,
                "unit_price": 2.2,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 8.0,
                "unit_price": 3.2,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 7.8,
                "unit_price": 3.12,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 8.5,
                "unit_price": 3.4,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 2600,
            "fat_g": 55.0,
            "saturated_fat_g": 4.0,
            "sugars_g": 4.5,
            "proteins_g": 21.0,
            "salt_g": 0.05
        }
    },
    {
        "id": "chia_seeds_350g",
        "name": "Organic Black Chia Seeds 350g",
        "variant": "Raw Superfood",
        "health_rating": 5.0,
        "stores": [
            {
                "store": "ALDI",
                "price": 3.9,
                "unit_price": 1.11,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 6.0,
                "unit_price": 1.71,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 5.8,
                "unit_price": 1.66,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 6.4,
                "unit_price": 1.83,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 1850,
            "fat_g": 31.0,
            "saturated_fat_g": 3.3,
            "sugars_g": 0.0,
            "proteins_g": 17.0,
            "salt_g": 0.04
        }
    },
    {
        "id": "macadamia_nuts_200g",
        "name": "Australian Roasted Macadamia Nuts 200g",
        "variant": "Lightly Salted",
        "health_rating": 4.5,
        "stores": [
            {
                "store": "ALDI",
                "price": 6.9,
                "unit_price": 3.45,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 10.0,
                "unit_price": 5.0,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 9.8,
                "unit_price": 4.9,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 10.5,
                "unit_price": 5.25,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 3000,
            "fat_g": 76.0,
            "saturated_fat_g": 12.0,
            "sugars_g": 4.5,
            "proteins_g": 8.0,
            "salt_g": 0.5
        }
    },
    {
        "id": "coconut_water_1l",
        "name": "CocoXpress Pure Coconut Water 1L",
        "variant": "100% Pure Natural",
        "health_rating": 4.5,
        "stores": [
            {
                "store": "ALDI",
                "price": 2.9,
                "unit_price": 0.29,
                "unit": "100ml"
            },
            {
                "store": "Coles",
                "price": 4.5,
                "unit_price": 0.45,
                "unit": "100ml"
            },
            {
                "store": "Woolworths",
                "price": 4.3,
                "unit_price": 0.43,
                "unit": "100ml"
            },
            {
                "store": "IGA",
                "price": 4.8,
                "unit_price": 0.48,
                "unit": "100ml"
            }
        ],
        "nutriments": {
            "energy_kj": 80,
            "fat_g": 0.0,
            "saturated_fat_g": 0.0,
            "sugars_g": 4.5,
            "proteins_g": 0.0,
            "salt_g": 0.05
        }
    },
    {
        "id": "protein_powder_1kg",
        "name": "Whey Protein Concentrate Powder 1kg",
        "variant": "Vanilla Ice Cream Flavor",
        "health_rating": 4.0,
        "stores": [
            {
                "store": "ALDI",
                "price": 24.9,
                "unit_price": 2.49,
                "unit": "100g"
            },
            {
                "store": "Coles",
                "price": 35.0,
                "unit_price": 3.5,
                "unit": "100g"
            },
            {
                "store": "Woolworths",
                "price": 34.0,
                "unit_price": 3.4,
                "unit": "100g"
            },
            {
                "store": "IGA",
                "price": 37.0,
                "unit_price": 3.7,
                "unit": "100g"
            }
        ],
        "nutriments": {
            "energy_kj": 1600,
            "fat_g": 5.5,
            "saturated_fat_g": 3.0,
            "sugars_g": 4.5,
            "proteins_g": 75.0,
            "salt_g": 0.35
        }
    }
]

# === Image URL Dictionary, to be fetched from a image hosting service ===
IMAGE_URLS = {
    "siftLogo": "https://i.postimg.cc/sxK3K7MK/Sift-Logo.png",
    "tabMain": "https://i.postimg.cc/KjQmQB1z/House.png",
    "tabMap": "https://i.postimg.cc/vTXGXf4m/Map.png",
    "tabSettings": "https://i.postimg.cc/1XMyMw83/Settings.png",
    "themeLight": "https://i.postimg.cc/1XMyMw8g/Light-Mode.png",
    "themeDark": "https://i.postimg.cc/Hn3T3Xrr/Dark-Mode.png",
    "themeProDuo": "https://i.postimg.cc/T1QTQgKp/Pro-Duo-Mode.png",
    "themeInvert": "https://i.postimg.cc/prkPkzmn/Invert-Mode.png",
    "userAvatar": "https://i.postimg.cc/d3Jq84Vh/User-Avatar.png",
    "guestAvatar": "https://i.postimg.cc/SRVmVCny/Guest-Avatar.png"
}

PAGE_MAIN_ELEMENTS = []
PAGE_MAP_ELEMENTS = []
PAGE_SETTINGS_ELEMENTS = []

# === User Account Database File ===
DB_FILE = "sift_users.json"

# === Session Data Dictionary ===
SESSION_DATA = {
    "is_logged_in": False,
    "user_id": "SIFT-2026-GUEST",
    "passcode": "",
    "display_name": "Guest Account"
}

def save_user_to_database(display_name, passcode, preferences_dict = None):
    if preferences_dict is None:
        if 'settings_page' in globals():
            preferences_dict = {
                "default_theme": current_theme_name,
                "default_sort": globals()['settings_page'].sorting_var.get()
            }
        else:
            preferences_dict = {
                "default_theme": "light",
                "default_sort": "Relevance"
            }

    user_id = f"SIFT-{str(uuid.uuid4())[:4].upper()}-{str(uuid.uuid4())[:1].upper()}"
    account_payload = {
        "is_logged_in": True,
        "user_id": user_id,
        "passcode": passcode,
        "display_name": display_name,
        "preferences": preferences_dict
    }

    with open(DB_FILE, "w") as file:
        json.dump(account_payload, file, indent=4)

    return account_payload

def load_user_from_database():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r") as file:
                data = json.load(file)
            data["is_logged_in"] = True

            if "preferences" not in data:
                data["preferences"] = {"default_theme": "light", "default_sort": "Relevance"}
            return data
        except Exception:
            pass

    return {
        "is_logged_in": False,
        "user_id": f"SIFT-{str(uuid.uuid4())[:4].upper()}-GUEST",
        "passcode": "",
        "display_name": "Guest Account",
        "preferences": {
            "default_theme": "light",
            "default_sort": "Relevance"
        }
    }

SESSION_DATA = load_user_from_database()

# === Camera Scanner Class ===
class AdvancedCameraScanner:
    def __init__(self, canvas):
        self.canvas = canvas
        self.camera_stream = None
        self.is_scanning = False
        self.current_frame = None

    def trigger_scan(self):
        if self.is_scanning:
            return
        self.is_scanning = True
        self.current_frame = None

        self.camera_stream = cv2.VideoCapture(0)
        if not self.camera_stream.isOpened():
            self.is_scanning = False
            return

        scanner_thread = threading.Thread(target=self._run_hardware_capture_loop, daemon=True)
        scanner_thread.start()

        root.after(10, self._initialize_main_thread_window_viewer)

    def _run_hardware_capture_loop(self):
        while self.is_scanning and self.camera_stream:
            success, frame = self.camera_stream.read()
            if not success:
                break

            self.current_frame = frame.copy()

            scanned_barcodes = decode(frame)
            for barcode in scanned_barcodes:
                barcode_number = barcode.data.decode('utf-8')

                self.is_scanning = False
                if self.camera_stream:
                    self.camera_stream.release()

                root.after(1, cv2.destroyAllWindows)

                self._fetch_product_from_remote_api(barcode_number)
                return

            time.sleep(0.01)

    def _initialize_main_thread_window_viewer(self):
        if not self.is_scanning or not self.camera_stream:
            cv2.destroyAllWindows()
            return

        if self.current_frame is not None:
            frame_preview = self.current_frame.copy()

            scanned_barcodes = decode(frame_preview)
            for barcode in scanned_barcodes:
                (x, y, w, h) = barcode.rect
                cv2.rectangle(frame_preview, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame_preview, "PROCESSING DATA...", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            cv2.imshow("Sift Scanner Frame - Keep Barcode Intact", frame_preview)

            if cv2.waitKey(1) & 0xFF == 27:
                self.is_scanning = False
                if self.camera_stream:
                    self.camera_stream.release()
                cv2.destroyAllWindows()
                return

        if self.is_scanning:
            root.after(16, self._initialize_main_thread_window_viewer)
        else:
            cv2.destroyAllWindows()

    def _fetch_product_from_remote_api(self, barcode_value):
        requested_fields = "product_name,brands,ecoscore_grade,nutriscore_grade,nova_group,nutriments"
        api_endpoint_target = f"https://world.openfoodfacts.org/api/v2/product/{barcode_value}.json?fields={requested_fields}"
        headers = { "User-Agent": "Sift/0.6.13 (weDontHaveAnEmail@thankYouForYourAPI.com)" }

        try:
            response = requests.get(api_endpoint_target, headers=headers, timeout=5)
            if response.status_code == 200:
                json_payload = response.json()
                if "product" in json_payload:
                    product_data = json_payload["product"]
                    item_name = product_data.get("product_name", "Unknown Item")
                    brand_name = product_data.get("brands", "Local Source")
                    eco_grade = str(product_data.get("ecoscore_grade", "N/A")).upper()
                    nutri_grade = str(product_data.get("nutriscore_grade", "N/A")).upper()
                    nova_group = product_data.get("nova_group", "N/A")

                    raw_nutriments = product_data.get("nutriments", {})
                    nutrition_payload = {
                        "energy_kj": float(raw_nutriments.get("energy-kj_100g", 0.0)),
                        "fat_g": float(raw_nutriments.get("fat_100g", 0.0)),
                        "saturated_fat_g": float(raw_nutriments.get("saturated-fat_100g", 0.0)),
                        "sugars_g": float(raw_nutriments.get("sugars_100g", 0.0)),
                        "proteins_g": float(raw_nutriments.get("proteins_100g", 0.0)),
                        "salt_g": float(raw_nutriments.get("salt_100g", 0.0))
                    }

                    parsed_result = {
                        "name": f"{item_name} ({brand_name})",
                        "desc": f"EcoScore Grade: {eco_grade} | NutriScore: {nutri_grade}\nNOVA Processing Group Tier: {nova_group}",
                        "nutriments": nutrition_payload
                    }
                    self._push_data_to_main_thread_ui(parsed_result)
                    return

            self._push_data_to_main_thread_ui({
                "name": "Unindexed Grocery Item",
                "desc": f"Code: {barcode_value}\nNo data.",
                "nutriments": {"energy_kj": 0.0, "fat_g": 0.0, "saturated_fat_g": 0.0, "sugars_g": 0.0, "proteins_g": 0.0, "salt_g": 0.0}
            })
        except Exception as network_exception:
            self._push_data_to_main_thread_ui({
                "name": "Network Request Failure",
                "desc": f"Check your local internet connection: {str(network_exception)}",
                "nutriments": {"energy_kj": 0.0, "fat_g": 0.0, "saturated_fat_g": 0.0, "sugars_g": 0.0, "proteins_g": 0.0, "salt_g": 0.0}
            })

    def _push_data_to_main_thread_ui(self, formatted_product_dict):
        def apply_canvas_text_changes():
            global USER_CART
            full_product_name = formatted_product_dict["name"]
            raw_description = formatted_product_dict["desc"]
            nutrient_data = formatted_product_dict["nutriments"]

            try:
                store_vendor_string = full_product_name.split("(")[-1].replace(")", "").strip()
            except Exception:
                store_vendor_string = "API Verified"

            USER_CART.append({
                "name": full_product_name,
                "store": store_vendor_string if full_product_name != "Unindexed Grocery Item" else raw_description,
                "price": 0.00,
                "description_label": raw_description,
                "nutriments": nutrient_data
            })

            if 'dashboard_engine' in globals():
                globals()['dashboard_engine'].render_cart_items()
            if 'search_overlay' in globals():
                globals()['search_overlay'].dismiss_search_interface()

        root.after(1, apply_canvas_text_changes)

# === Profile Slide Menu Class ===
class ProfileSlideMenu:
    def __init__(self, canvas, width, height):
        self.canvas = canvas
        self.width = width
        self.height = height
        self.current_x = -400
        self.target_x = -400
        self.is_moving = False

        self.panel_id = canvas.create_rectangle(self.current_x, 0, self.current_x + 300, height, width=1)
        self.avatar_id = canvas.create_image(self.current_x + 150, 120, image="", anchor="center")
        self.avatar_references = {}
        self.load_avatar_images()

        self.txt_title = canvas.create_text(self.current_x + 150, 180, text="", font=("Helvetica Neue", 16, "bold"), anchor="center")
        self.txt_id = canvas.create_text(self.current_x + 30, 230, text="", font=("Helvetica Neue", 11), anchor="nw")
        self.txt_pass = canvas.create_text(self.current_x + 30, 260, text="", font=("Helvetica Neue", 11), anchor="nw")

        self.btn_action = canvas.create_line(self.current_x + 40, 640, self.current_x + 260, 640, width=35, capstyle="round")
        self.txt_action = canvas.create_text(self.current_x + 150, 640, text="", font=("Helvetica Neue", 11, "bold"), anchor="center")

        self.all_elements = (self.panel_id, self.avatar_id, self.txt_title, self.txt_id, self.txt_pass, self.btn_action, self.txt_action)

        self.canvas.tag_bind(self.btn_action, "<Button-1>", self.handle_action_click)
        self.canvas.tag_bind(self.txt_action, "<Button-1>", self.handle_action_click)

        self.form_elements = []
        self.entry_name = None
        self.entry_pass = None

        self.update_colors()

    def load_avatar_images(self):
        avatar_url_map = {"user": "userAvatar", "guest": "guestAvatar"}
        for key in ["user", "guest"]:
            url_key = avatar_url_map[key]
            url_string = IMAGE_URLS.get(url_key, None)
            try:
                response = requests.get(url_string, timeout=4)
                img_pil = Image.open(io.BytesIO(response.content)).convert("RGBA").resize((80, 80), Image.Resampling.LANCZOS)
                self.avatar_references[key] = ImageTk.PhotoImage(img_pil)
            except Exception as e:
                blank = ImageTk.PhotoImage(Image.new("RGBA", (1, 1), (0, 0, 0, 0)))
                self.avatar_references[key] = blank

    def handle_action_click(self, event):
        global SESSION_DATA
        if SESSION_DATA["is_logged_in"]:
            if os.path.exists(DB_FILE):
                os.remove(DB_FILE)
            SESSION_DATA = {
                "is_logged_in": False,
                "user_id": f"SIFT-{str(uuid.uuid4())[:4].upper()}-GUEST",
                "passcode": "",
                "display_name": "Guest Account"
            }
            self.update_colors()
            self.toggle(open_panel=True)
        else:
            self.toggle(open_panel=False)
            self.canvas.after(250, self.display_registration_form_overlay)

    def display_registration_form_overlay(self):
        theme = THEMES[current_theme_name]
        form_bg = self.canvas.create_rectangle(30, 160, 380, 540, fill=theme["card_bg"], outline=theme["card_bg"], width=1)
        form_title = self.canvas.create_text(205, 200, text="Create Account", font=("Helvetica Neue", 20, "bold"), fill=theme["text"], anchor="center")

        lbl_name = self.canvas.create_text(60, 245, text="Username / Display Name", font=("Helvetica Neue", 11, "bold"), fill=theme["accent"], anchor="nw")
        lbl_pass = self.canvas.create_text(60, 335, text="Passcode (6+ Characters)", font=("Helvetica Neue", 11, "bold"), fill=theme["accent"], anchor="nw")

        def validate_limit(P):
            return len(P) <= 20

        vcmd = (self.canvas.master.register(validate_limit), '%P')

        self.entry_name = tk.Entry(
            self.canvas.master,
            font=("Helvetica Neue", 12),
            bg=theme["bg"],
            fg=theme["text"],
            bd=0,
            highlightthickness=1,
            highlightcolor=theme["accent"],
            validate="key",
            validatecommand=vcmd
        )

        self.entry_pass = tk.Entry(
            self.canvas.master,
            font=("Helvetica Neue", 12),
            bg=theme["bg"],
            fg=theme["text"],
            bd=0,
            highlightthickness=1,
            highlightcolor=theme["accent"],
            show="*",
            validate="key",
            validatecommand=vcmd)

        window_name = self.canvas.create_window(205, 290, window=self.entry_name, width=290, height=32)
        window_pass = self.canvas.create_window(205, 380, window=self.entry_pass, width=290, height=32)

        btn_submit = self.canvas.create_line(125, 460, 285, 460, width=35, fill=theme["btn_bg"], capstyle="round")
        txt_submit = self.canvas.create_text(205, 460, text="Register Profile", font=("Helvetica Neue", 11, "bold"), fill=theme["btn_txt"], anchor="center")
        btn_cancel = self.canvas.create_text(205, 510, text="Cancel", font=("Helvetica Neue", 11), fill="#FF3B30", anchor="center")

        self.form_elements.extend([form_bg, form_title, lbl_name, lbl_pass, window_name, window_pass, btn_submit, txt_submit, btn_cancel])

        self.canvas.tag_bind(btn_submit, "<Button-1>", self.process_registration_form_submission)
        self.canvas.tag_bind(txt_submit, "<Button-1>", self.process_registration_form_submission)
        self.canvas.tag_bind(btn_cancel, "<Button-1>", lambda e: self.terminate_registration_form_overlay())

    def process_registration_form_submission(self, event):
        global SESSION_DATA
        typed_name = self.entry_name.get().strip()
        typed_pass = self.entry_pass.get().strip()
        if len(typed_name) < 2 or len(typed_pass) < 1:
            return
        hidden_passcode_string = "*" * len(typed_pass)
        SESSION_DATA = save_user_to_database(typed_name, hidden_passcode_string)
        self.terminate_registration_form_overlay()
        self.update_colors()
        self.toggle(open_panel=True)

    def terminate_registration_form_overlay(self):
        for element_id in self.form_elements:
            self.canvas.delete(element_id)
        self.form_elements.clear()
        self.entry_name = None
        self.entry_pass = None

    def update_colors(self):
        theme = THEMES[current_theme_name]
        self.canvas.itemconfig(self.panel_id, fill=theme["card_bg"], outline=theme["card_bg"])
        self.canvas.itemconfig(self.txt_title, fill=theme["text"], text=SESSION_DATA["display_name"])

        if SESSION_DATA["is_logged_in"]:
            self.canvas.itemconfig(self.avatar_id, image=self.avatar_references["user"])
            self.canvas.itemconfig(self.txt_id, text=f"User ID: {SESSION_DATA['user_id']}", fill=theme["text"])
            self.canvas.itemconfig(self.txt_pass, text=f"Passcode: {SESSION_DATA['passcode']}", fill=theme["text"])
            self.canvas.itemconfig(self.btn_action, fill="#FF3B30")
            self.canvas.itemconfig(self.txt_action, text="Sign Out Account", fill="#FFFFFF")
        else:
            self.canvas.itemconfig(self.avatar_id, image=self.avatar_references["guest"])
            self.canvas.itemconfig(self.txt_id, text="Sign in to sync your\nhistorical data summaries across devices.", fill=theme["accent"])
            self.canvas.itemconfig(self.txt_pass, text="")
            self.canvas.itemconfig(self.btn_action, fill=theme["btn_bg"])
            self.canvas.itemconfig(self.txt_action, text="Create Account", fill=theme["btn_txt"])

    def toggle(self, open_panel=True):
        self.target_x = 0 if open_panel else -310
        self.update_colors()
        self.lift_panel_stack()
        if not self.is_moving:
            self.step_slide()

    def lift_panel_stack(self):
        for eid in self.all_elements:
            self.canvas.lift(eid)
        for fid in self.form_elements:
            self.canvas.lift(fid)

    def step_slide(self):
        diff = self.target_x - self.current_x
        if abs(diff) < 1:
            self.current_x = self.target_x
            self.is_moving = False
        else:
            self.is_moving = True
            step_move = diff * 0.25
            self.current_x += step_move
            for eid in self.all_elements:
                self.canvas.move(eid, step_move, 0)
            self.lift_panel_stack()
            self.canvas.after(16, self.step_slide)

# === Slide Menu Class, called by AnimatedCapsuleButton ===
import tkinter as tk
from tkinter import ttk

class SlideMenu:
    def __init__(self, canvas, width, height):
        self.canvas = canvas
        self.width = width
        self.height = height

        self.current_x = width + 20
        self.target_x = width + 20
        self.is_moving = False

        self.panel_id = canvas.create_rectangle(
            self.current_x, 0, self.current_x + width, height,
            fill="#FFFFFF", outline="#E5E5EA", width=1
        )

        self.title_id = canvas.create_text(
            self.current_x + 25, 50,
            text="Product Analytics", font=("Helvetica Neue", 22, "bold"), fill="#000000", anchor="nw"
        )

        self.container_frame = tk.Frame(self.canvas.master, bd=0)

        self.scroll_canvas = tk.Canvas(self.container_frame, bg="#FFFFFF", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.container_frame, orient="vertical", command=self.scroll_canvas.yview)

        self.inner_scroll_frame = tk.Frame(self.scroll_canvas, bg="#FFFFFF")
        self.inner_scroll_frame.bind(
            "<Configure>",
            lambda e: self.scroll_canvas.configure(scrollregion=self.scroll_canvas.bbox("all"))
        )

        self.scroll_canvas.create_window((0, 0), window=self.inner_scroll_frame, anchor="nw", width=255)
        self.scroll_canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.scroll_canvas.pack(side="left", fill="both", expand=True)

        self.window_id = self.canvas.create_window(
            self.current_x + 150, 360, window=self.container_frame, width=270, height=520, state="normal"
        )

    def toggle(self, open_panel=True):
        self.target_x = (self.width - 300) if open_panel else (self.width + 20)

        if open_panel:
            self.generate_product_widget_cards()

        self.lift_panel_stack()
        if not self.is_moving:
            self.step_slide()

    def generate_product_widget_cards(self):
        global USER_CART
        theme = THEMES[current_theme_name]

        for child in self.inner_scroll_frame.winfo_children():
            child.destroy()

        if not USER_CART:
            no_data_lbl = tk.Label(
                self.inner_scroll_frame,
                text="Your sustainable grocery cart\nis empty.\n\nScan barcodes to log metrics.",
                font=("Helvetica Neue", 11, "italic"), fg=theme["accent"], bg=theme["card_bg"], pady=40
            )
            no_data_lbl.pack(fill="x", expand=True)
            return

        for idx, item in enumerate(USER_CART):
            item_name = item.get("name", "Unknown Grocery Product")
            store_vendor = item.get("store", "Verified Source")
            grades_line = item.get("description_label", "Eco Metrics Verified")
            macros = item.get("nutriments", {})

            card_widget = tk.Frame(self.inner_scroll_frame, bg=theme["bg"], bd=0, relief="solid", padx=10, pady=10)
            card_widget.pack(fill="x", expand=True, pady=8, padx=5)

            lbl_title = tk.Label(
                card_widget, text=f"{idx + 1}. {item_name}",
                font=("Helvetica Neue", 11, "bold"), fg=theme["text"], bg=theme["bg"], anchor="w", justify="left"
            )
            lbl_title.pack(fill="x")

            lbl_vendor = tk.Label(
                card_widget, text=f"Vendor: {store_vendor}",
                font=("Helvetica Neue", 9, "italic"), fg=theme["accent"], bg=theme["bg"], anchor="w"
            )
            lbl_vendor.pack(fill="x", pady=(0, 4))

            lbl_grades = tk.Label(
                card_widget, text=grades_line,
                font=("Helvetica Neue", 9, "bold"), fg="#007AFF" if current_theme_name != "inverted" else theme["blue_txt"],
                bg=theme["bg"], anchor="w", justify="left"
            )
            lbl_grades.pack(fill="x", pady=(0, 6))

            grid_frame = tk.Frame(card_widget, bg=theme["bg"])
            grid_frame.pack(fill="x", pady=2)

            nutrient_rows = [
                ("Energy (kJ)", f"{macros.get('energy_kj', 0.0):.1f} kJ"),
                ("Total Fats", f"{macros.get('fat_g', 0.0):.1f} g"),
                ("  ↳ Sat. Fat", f"{macros.get('saturated_fat_g', 0.0):.1f} g"),
                ("Sugars", f"{macros.get('sugars_g', 0.0):.1f} g"),
                ("Proteins", f"{macros.get('proteins_g', 0.0):.1f} g"),
                ("Salt / Sodium", f"{macros.get('salt_g', 0.0):.2f} g")
            ]

            for row_idx, (label, val) in enumerate(nutrient_rows):
                lbl_name = tk.Label(grid_frame, text=label, font=("Helvetica Neue", 9), fg=theme["text"], bg=theme["bg"], anchor="w")
                lbl_val = tk.Label(grid_frame, text=val, font=("Helvetica Neue", 9, "bold"), fg=theme["text"], bg=theme["bg"], anchor="e")

                lbl_name.grid(row=row_idx, column=0, sticky="w", pady=1)
                lbl_val.grid(row=row_idx, column=1, sticky="e", pady=1)
                grid_frame.columnconfigure(1, weight=1)

    def lift_panel_stack(self):
        self.canvas.lift(self.panel_id)
        self.canvas.lift(self.title_id)
        self.canvas.lift(self.window_id)

    def step_slide(self):
        diff = self.target_x - self.current_x
        if abs(diff) < 1:
            self.current_x = self.target_x
            self.is_moving = False

            self.canvas.coords(self.panel_id, self.current_x, 0, self.current_x + self.width, self.height)
            self.canvas.coords(self.title_id, self.current_x + 25, 50)
            self.canvas.coords(self.window_id, self.current_x + 150, 360)
        else:
            self.is_moving = True
            step_move = diff * 0.25
            self.current_x += step_move

            self.canvas.move(self.panel_id, step_move, 0)
            self.canvas.move(self.title_id, step_move, 0)
            self.canvas.move(self.window_id, step_move, 0)

            self.lift_panel_stack()
            self.canvas.after(16, self.step_slide)

    def update_colors(self):
        theme = THEMES[current_theme_name]

        self.canvas.itemconfig(self.panel_id, fill=theme["card_bg"], outline=theme["card_bg"])
        self.canvas.itemconfig(self.title_id, fill=theme["text"])

        self.container_frame.configure(bg=theme["card_bg"])
        self.scroll_canvas.configure(bg=theme["card_bg"])
        self.inner_scroll_frame.configure(bg=theme["card_bg"])

        if self.canvas.itemcget(self.panel_id, "state") != "hidden" and self.current_x < self.width:
            self.generate_product_widget_cards()

# === Theme Dropdown Class ===
class HorizontalThemeDropdown:
    def __init__(self, canvas, anchor_x, anchor_y):
        self.canvas = canvas
        self.anchor_x = anchor_x
        self.anchor_y = anchor_y
        self.current_width = 0
        self.target_width = 160
        self.is_animating = False
        self.is_open = False

        self.tray_id = canvas.create_rectangle(
            anchor_x, anchor_y - 16, anchor_x, anchor_y + 16,
            width=0, fill="", outline=""
        )

        self.modes = ["light", "dark", "pro-duo", "invert"]
        self.btn_ids = []
        self.img_ids = []
        self.icon_light_cache = {}
        self.icon_dark_cache = {}

        self.load_and_process_assets()

        for idx, label in enumerate(self.modes):
            b_id = canvas.create_line(anchor_x, anchor_y, anchor_x, anchor_y, width=0, fill="", capstyle="round")
            i_id = canvas.create_image(anchor_x, anchor_y, image="", anchor="center")
            self.btn_ids.append(b_id)
            self.img_ids.append(i_id)
            self.setup_click_events(b_id, i_id, label)

        self.update_colors()

    def load_and_process_assets(self):
        theme_url_map = {
            "light": "themeLight",
            "dark": "themeDark",
            "pro-duo": "themeProDuo",
            "invert": "themeInvert"
        }
        for label in self.modes:
            url_key = theme_url_map.get(label, None)
            url_string = IMAGE_URLS.get(url_key, None)
            try:
                response = requests.get(url_string, timeout=4)
                img_pil_orig = Image.open(io.BytesIO(response.content)).convert("RGBA").resize((16, 16), Image.Resampling.LANCZOS)
                self.icon_light_cache[label] = ImageTk.PhotoImage(img_pil_orig)

                r, g, b, a = img_pil_orig.split()
                r_inv = r.point(lambda p: 255 - p)
                g_inv = g.point(lambda p: 255 - p)
                b_inv = b.point(lambda p: 255 - p)
                img_inverted_pil = Image.merge("RGBA", (r_inv, g_inv, b_inv, a))
                self.icon_dark_cache[label] = ImageTk.PhotoImage(img_inverted_pil)
            except Exception as e:
                blank = ImageTk.PhotoImage(Image.new("RGBA", (1, 1), (0, 0, 0, 0)))
                self.icon_light_cache[label] = blank
                self.icon_dark_cache[label] = blank

    def setup_click_events(self, b_id, i_id, label):
        def trigger_swap(event):
            global current_theme_name
            if label == "pro-duo":
                current_theme_name = "pro-duo-triteranopia"
            elif label == "invert":
                current_theme_name = "inverted"
            else:
                current_theme_name = label
            update_system_wide_themes()
            self.toggle(force_close=True)

        self.canvas.tag_bind(b_id, "<Button-1>", trigger_swap)
        self.canvas.tag_bind(i_id, "<Button-1>", trigger_swap)

    def update_colors(self):
        if self.is_open or self.current_width > 1:
            theme = THEMES[current_theme_name]
            self.canvas.itemconfig(self.tray_id, fill="", outline="", width=0)
            use_inverted_assets = current_theme_name in ["dark", "inverted"]
            active_cache = self.icon_dark_cache if use_inverted_assets else self.icon_light_cache

            for b_id in self.btn_ids:
                self.canvas.itemconfig(b_id, fill=theme["bg"], width=22)
            for idx, i_id in enumerate(self.img_ids):
                label = self.modes[idx]
                self.canvas.itemconfig(i_id, image=active_cache[label])
        else:
            self.canvas.itemconfig(self.tray_id, fill="", outline="", width=0)
            for b_id in self.btn_ids:
                self.canvas.itemconfig(b_id, fill="", width=0)
            for i_id in self.img_ids:
                self.canvas.itemconfig(i_id, image="")

    def toggle(self, force_close=False):
        if self.is_open or force_close:
            self.target_width = 0
            self.is_open = False
        else:
            self.target_width = 160
            self.is_open = True
            self.lift_tray_stack()
        if not self.is_animating:
            self.step_tray_expansion()

    def lift_tray_stack(self):
        if self.current_width > 1:
            self.canvas.lift(self.tray_id)
            for b_id in self.btn_ids: self.canvas.lift(b_id)
            for i_id in self.img_ids: self.canvas.lift(i_id)

    def step_tray_expansion(self):
        diff = self.target_width - self.current_width
        if abs(diff) < 1:
            self.current_width = self.target_width
            self.is_animating = False
            if self.current_width == 0:
                self.update_colors()
        else:
            self.is_animating = True
            self.current_width += diff * 0.25
            self.canvas.after(16, self.step_tray_expansion)
            if self.current_width > 1:
                self.update_colors()

        x_start = self.anchor_x - self.current_width
        self.canvas.coords(self.tray_id, x_start, self.anchor_y - 16, self.anchor_x, self.anchor_y + 16)

        segment = self.current_width / 4
        for i in range(4):
            if self.current_width > 1:
                btn_center_x = self.anchor_x - (segment * i) - (segment / 2)
                self.canvas.coords(self.btn_ids[i], btn_center_x - 14, self.anchor_y, btn_center_x + 14, self.anchor_y)
                self.canvas.coords(self.img_ids[i], btn_center_x, self.anchor_y)
            else:
                self.canvas.coords(self.btn_ids[i], self.anchor_x, self.anchor_y, self.anchor_x, self.anchor_y)
                self.canvas.coords(self.img_ids[i], self.anchor_x, self.anchor_y)

        self.lift_tray_stack()

# === Animated Capsule Button Class, calls SlideMenu ===
class AnimatedCapsuleButton:
    def __init__(self, canvas, x1, y1, x2, y2, fill_color, text, command, base_width=40):
        self.canvas = canvas
        self.orig_x1, self.orig_y1 = x1, y1
        self.orig_x2, self.orig_y2 = x2, y2
        self.base_width = base_width
        self.fill_color = fill_color
        self.command = command
        self.center_x = (x1 + x2) / 2
        self.center_y = (y1 + y2) / 2
        self.current_scale = 1.0
        self.target_scale = 1.0
        self.is_animating = False

        self.line_id = canvas.create_line(x1, y1, x2, y2, fill=fill_color, width=base_width, capstyle="round")
        self.text_id = canvas.create_text(self.center_x, self.center_y, text=text, font=("Helvetica Neue", 13, "bold"), fill="#FFFFFF", anchor="center")

        for element_id in (self.line_id, self.text_id):
            self.canvas.tag_bind(element_id, "<ButtonPress-1>", self.on_press)
            self.canvas.tag_bind(element_id, "<ButtonRelease-1>", self.on_release)
            self.canvas.tag_bind(element_id, "<Enter>", self.on_hover)
            self.canvas.tag_bind(element_id, "<Leave>", self.on_leave)

    def on_hover(self, event):
        self.canvas.itemconfig(self.line_id, fill="#3A3A3C")

    def on_leave(self, event):
        theme = THEMES[current_theme_name]
        self.canvas.itemconfig(self.line_id, fill=theme["btn_bg"])
        self.animate_to_scale(1.0)

    def on_press(self, event):
        self.canvas.itemconfig(self.line_id, fill="#1C1C1E")
        self.animate_to_scale(0.95)

    def on_release(self, event):
        self.canvas.itemconfig(self.line_id, fill="#3A3A3C")
        self.animate_to_scale(1.0)
        self.command()

    def animate_to_scale(self, target):
        self.target_scale = target
        if not self.is_animating:
            self.step_scale_animation()

    def step_scale_animation(self):
        diff = self.target_scale - self.current_scale
        if abs(diff) < 0.005:
            self.current_scale = self.target_scale
            self.is_animating = False
        else:
            self.is_animating = True
            self.current_scale += diff * 0.4
            self.canvas.after(16, self.step_scale_animation)

        new_x1 = self.center_x + (self.orig_x1 - self.center_x) * self.current_scale
        new_y1 = self.center_y + (self.orig_y1 - self.center_y) * self.current_scale
        new_x2 = self.center_x + (self.orig_x2 - self.center_x) * self.current_scale
        new_y2 = self.center_y + (self.orig_y2 - self.center_y) * self.current_scale

        self.canvas.coords(self.line_id, new_x1, new_y1, new_x2, new_y2)
        self.canvas.itemconfig(self.line_id, width=int(self.base_width * self.current_scale))
        scaled_font_size = int(13 * self.current_scale)
        self.canvas.itemconfig(self.text_id, font=("Helvetica Neue", scaled_font_size, "bold"))
        self.keep_layered_under()

    def keep_layered_under(self):
        try:
            self.canvas.tag_lower(self.line_id, product_panel.panel_id)
            self.canvas.tag_lower(self.text_id, product_panel.panel_id)
            self.canvas.tag_lower(self.line_id, profile_menu.panel_id)
            self.canvas.tag_lower(self.text_id, profile_menu.panel_id)
        except NameError:
            pass

    def update_colors(self):
        theme = THEMES[current_theme_name]
        self.canvas.itemconfig(self.line_id, fill=theme["btn_bg"])
        self.canvas.itemconfig(self.text_id, fill=theme["btn_txt"])

# === System-Wide Theme Update Function, called by HorizontalThemeDropdown ===
def update_system_wide_themes():
    theme = THEMES[current_theme_name]

    master_bg.configure(bg=theme["bg"])
    master_bg.itemconfig(chassis_rect1, fill=theme["bg"], outline=theme["bg"])
    master_bg.itemconfig(chassis_rect2, fill=theme["bg"], outline=theme["bg"])
    master_bg.itemconfig(chassis_island, fill=theme["island"])
    master_bg.itemconfig(corner_tl, fill=theme["bg"], outline=theme["bg"])
    master_bg.itemconfig(corner_tr, fill=theme["bg"], outline=theme["bg"])
    master_bg.itemconfig(corner_bl, fill=theme["bg"], outline=theme["bg"])
    master_bg.itemconfig(corner_br, fill=theme["bg"], outline=theme["bg"])

    master_bg.itemconfig(txt_clock, fill=theme["text"])
    master_bg.itemconfig(txt_battery, fill=theme["text"])
    master_bg.itemconfig(txt_logo, fill=theme["text"])

    compare_btn.update_colors()
    product_panel.update_colors()
    profile_menu.update_colors()
    theme_dropdown.update_colors()

    master_bg.itemconfig(btn_profile_bg, fill=theme["card_bg"], outline=theme["card_bg"])
    master_bg.itemconfig(txt_profile_icon, fill=theme["text"])
    master_bg.itemconfig(btn_theme_bg, fill=theme["card_bg"], outline=theme["card_bg"])

    try:
        lookup_key = current_theme_name
        if current_theme_name == "pro-duo-triteranopia":
            lookup_key = "pro-duo"
        elif current_theme_name == "inverted":
            lookup_key = "invert"

        use_inverted_assets = current_theme_name in ["dark", "inverted"]
        target_cache = theme_dropdown.icon_dark_cache if use_inverted_assets else theme_dropdown.icon_light_cache
        master_bg.itemconfig(logo_image_id, image=icon_dark_cache if current_theme_name == "inverted" else icon_light_cache)
        master_bg.itemconfig(img_theme_icon, image=target_cache[lookup_key])
    except NameError:
        pass

    try:
        compare_btn.update_colors()
    except NameError:
        pass
    try:
        product_panel.update_colors()
    except NameError:
        pass
    try:
        profile_menu.update_colors()
    except NameError:
        pass
    try:
        theme_dropdown.update_colors()
    except NameError:
        pass
    try:
        comparison_dashboard.update_colors()
    except NameError:
        pass
    try:
        bottom_nav_bar.update_colors()
    except NameError:
        pass
    try:
        map_page.update_colors()
    except NameError:
        pass
    try:
        search_popup_modal.update_colors()
    except NameError:
        pass
    try:
        settings_page.update_colors()
    except NameError:
        pass

def on_compare_trigger():
    product_panel.toggle(open_panel=True)

# === Background Click Handler, responsible for closing panels when clicking outside ===
def handle_background_click(event):
    if event.x > 320 and event.y > 85:
        profile_menu.toggle(open_panel=False)
    if event.x < 110:
        product_panel.toggle(open_panel=False)
    if event.y > 85:
        theme_dropdown.toggle(force_close=True)

# === Status Bar Update Function, updates clock and battery percentage every 10 seconds for realism ===
def update_status_bar():
    current_time = time.strftime("%H:%M")
    master_bg.itemconfig(txt_clock, text=current_time)
    try:
        battery = psutil.sensors_battery()
        percent = battery.percent if battery else 100
    except:
        percent = 100
    master_bg.itemconfig(txt_battery, text=f"{percent}%")
    root.after(10000, update_status_bar)

# === Page Route Change Handler, manages visibility of page elements based on the target page, called by BottomNavigationBar ===
def on_system_page_route_changed(target_page_name):
    if 'search_overlay' in globals():
        search_overlay.dismiss_search_interface()
    if 'search_popup_modal' in globals():
        search_popup_modal.dismiss_modal()

    master_bg.itemconfig("main_page", state="hidden")

    pages_map = {
        "Main": PAGE_MAIN_ELEMENTS,
        "Map": PAGE_MAP_ELEMENTS,
        "Settings": PAGE_SETTINGS_ELEMENTS
    }

    for page_name, elements_list in pages_map.items():
        if page_name == target_page_name:
            for element_id in elements_list:
                master_bg.itemconfig(element_id, state="normal")
        else:
            for element_id in elements_list:
                master_bg.itemconfig(element_id, state="hidden")

    if target_page_name == "Main":
        master_bg.itemconfig("main_page", state="normal")

    if target_page_name == "Settings":
        master_bg.itemconfig("settings_page", state="normal")

def draw_master_canvas(canvas, width, height, radius, color):
    global chassis_rect1, chassis_rect2, chassis_island, corner_tl, corner_tr, corner_bl, corner_br

    chassis_rect1 = canvas.create_rectangle(radius, 0, width - radius, height, fill=color, outline=color)
    chassis_rect2 = canvas.create_rectangle(0, radius, width, height - radius, fill=color, outline=color)

    outer_bg = "#1C1C1E"

    canvas.create_rectangle(0, 0, radius, radius, fill=outer_bg, outline=outer_bg)
    corner_tl = canvas.create_oval(0, 0, radius * 2, radius * 2, fill=color, outline=color)

    canvas.create_rectangle(width - radius, 0, width, radius, fill=outer_bg, outline=outer_bg)
    corner_tr = canvas.create_oval(width - (radius * 2), 0, width, radius * 2, fill=color, outline=color)

    canvas.create_rectangle(0, height - radius, radius, height, fill=outer_bg, outline=outer_bg)
    corner_bl = canvas.create_oval(0, height - (radius * 2), radius * 2, height, fill=color, outline=color)

    canvas.create_rectangle(width - radius, height - radius, width, height, fill=outer_bg, outline=outer_bg)
    corner_br = canvas.create_oval(width - (radius * 2), height - (radius * 2), width, height, fill=color, outline=color)

    canvas.create_line(width / 2 - 75, height - 20, width / 2 + 75, height - 20, fill="#3A3A3C", width=5, capstyle="round")
    chassis_island = canvas.create_line(155, 20, 255, 20, fill="#000000", width=22, capstyle="round")

# === Comparison Dashboard Class, displays cart items and alternative products ===
USER_CART = []
class ComparisonDashboard:
    def __init__(self, canvas, start_y=390):
        self.canvas = canvas
        self.start_y = start_y
        self.width = 370
        self.height = 190
        self.left_x = 20
        self.right_x = self.left_x + self.width
        self.center_x = (self.left_x + self.right_x) / 2
        self.radius = 16

        self.ui_elements = []
        self.alternative_rows = []
        self.cart_rows = []

        self.mock_alternatives = [
            {"name": "Organic Almond Milk", "price": "$2.20", "desc": "ALDI - Carbon Neutral, 100% Recyclable"},
            {"name": "Fairtrade Coffee Beans", "price": "$6.50", "desc": "ALDI - Zero Waste, Biodegradable Bag"},
            {"name": "Regenerative Flour", "price": "$3.40", "desc": "Woolworths - Soil-Health Sourced"}
        ]
        self.build_dashboard_layout()
        self.render_cart_items()

    def build_dashboard_layout(self):
        theme = THEMES[current_theme_name]
        x1, y1 = self.left_x, self.start_y
        x2, y2 = self.right_x, self.start_y + self.height
        r = self.radius

        points = [
            x1+r, y1,   x2-r, y1,   x2, y1,
            x2, y1+r,   x2, y2-r,   x2, y2,
            x2-r, y2,   x1+r, y2,   x1, y2,
            x1, y2-r,   x1, y1+r,   x1, y1
        ]

        self.card_bg = self.canvas.create_polygon(
            points, fill=theme["card_bg"], outline=theme["card_bg"], width=1, smooth=True, splinesteps=32, tags="main_page"
        )
        self.divider = self.canvas.create_line(
            self.center_x, self.start_y + 15, self.center_x, self.start_y + self.height - 15, tags="main_page",
            fill=theme["accent"], width=2
        )
        self.lbl_cart = self.canvas.create_text(
            self.left_x + 45, self.start_y + 20,
            text="Cart", font=("Helvetica Neue", 13, "bold"), fill=theme["text"], anchor="center", tags="main_page"
        )
        self.lbl_alternatives = self.canvas.create_text(
            self.center_x + 55, self.start_y + 20,
            text="Alternatives", font=("Helvetica Neue", 13, "bold"), fill=theme["text"], anchor="center", tags="main_page"
        )
        self.ui_elements.extend([self.card_bg, self.divider, self.lbl_cart, self.lbl_alternatives])

    def render_cart_items(self):
        theme = THEMES[current_theme_name]
        self.clear_cart_rows()

        is_hidden = self.canvas.itemcget(self.card_bg, "state") == "hidden"
        initial_state = "hidden" if is_hidden else "normal"

        row_y_start = self.start_y + 45
        row_height = 54
        row_spacing = 8

        for idx, item in enumerate(USER_CART[:2]):
            current_top_y = row_y_start + (idx * (row_height + row_spacing))
            current_bottom_y = current_top_y + row_height

            x1, y1 = self.left_x + 10, current_top_y
            x2, y2 = self.center_x - 10, current_bottom_y

            r = 12
            points = [
                x1+r, y1, x2-r, y1, x2, y1, x2, y1+r, x2, y2-r, x2, y2,
                x2-r, y2, x1+r, y2, x1, y2, x1, y2-r, x1, y1+r, x1, y1
            ]

            c_bg = self.canvas.create_polygon(
                points, fill=theme["bg"], outline=theme["bg"],
                width=1, smooth=True, splinesteps=32, tags="main_page", state=initial_state
            )

            raw_name = item["name"]
            display_name = f"{raw_name[:16]}..." if len(raw_name) > 19 else raw_name

            c_name = self.canvas.create_text(
                self.left_x + 22,
                current_top_y + 16,
                text=display_name,
                font=("Helvetica Neue", 10, "bold"),
                fill=theme["text"],
                anchor="w",
                tags="main_page",
                state=initial_state
            )

            c_store = self.canvas.create_text(
                self.left_x + 22,
                current_top_y + 36,
                text=f"📍 {item['store']}",
                font=("Helvetica Neue", 8, "normal"),
                fill=theme["accent"] if current_theme_name == "inverted" else "#8E8E93",
                anchor="w",
                tags="main_page",
                state=initial_state
            )

            c_price = self.canvas.create_text(
                self.center_x - 22,
                current_top_y + 36,
                text=f"${item['price']:.2f}",
                font=("Helvetica Neue", 10, "bold"),
                fill="#34C759" if current_theme_name != "inverted" else theme["green_txt"],
                anchor="e",
                tags="main_page",
                state=initial_state
            )

            self.cart_rows.extend([c_bg, c_name, c_store, c_price])

    def display_searched_alternatives(self):
        theme = THEMES[current_theme_name]
        self.clear_alternative_rows()
        row_y_start = self.start_y + 60

        for idx, item in enumerate(self.mock_alternatives):
            current_row_y = row_y_start + (idx * 40)
            r_bg = self.canvas.create_line(
                self.center_x + 10, current_row_y, self.right_x - 10, current_row_y,
                width=30, fill=theme["bg"], capstyle="round", tags="main_page"
            )
            r_txt = self.canvas.create_text(
                self.center_x + 20, current_row_y,
                text=item["name"], font=("Helvetica Neue", 9, "bold"), fill=theme["text"], anchor="w", tags="main_page"
            )
            r_price = self.canvas.create_text(
                self.right_x - 20, current_row_y,
                text=item["price"], font=("Helvetica Neue", 9, "bold"), fill="#34C759", anchor="e", tags="main_page"
            )

            self.alternative_rows.extend([r_bg, r_txt, r_price])
            self.setup_row_interaction(r_bg, r_txt, r_price, item)

    def setup_row_interaction(self, bg_id, text_id, price_id, data_payload):
        def on_item_selected(event):
            pass
        for element_id in (bg_id, text_id, price_id):
            self.canvas.tag_bind(element_id, "<Button-1>", on_item_selected)

    def clear_alternative_rows(self):
        for element_id in self.alternative_rows:
            self.canvas.delete(element_id)
        self.alternative_rows.clear()

    def clear_cart_rows(self):
        for element_id in self.cart_rows:
            self.canvas.delete(element_id)
        self.cart_rows.clear()

    def update_colors(self):
        theme = THEMES[current_theme_name]
        x1, y1 = self.left_x, self.start_y
        x2, y2 = self.right_x, self.start_y + self.height
        r = self.radius
        points = [
            x1+r, y1,   x2-r, y1,   x2, y1,
            x2, y1+r,   x2, y2-r,   x2, y2,
            x2-r, y2,   x1+r, y2,   x1, y2,
            x1, y2-r,   x1, y1+r,   x1, y1
        ]
        self.canvas.coords(self.card_bg, *points)
        self.canvas.itemconfig(
            self.card_bg,
            fill=theme["card_bg"],
            outline=theme["card_bg"],
            width=1
        )

        self.canvas.itemconfig(self.divider, fill=theme["accent"])
        self.canvas.itemconfig(self.lbl_cart, fill=theme["text"])
        self.canvas.itemconfig(self.lbl_alternatives, fill=theme["text"])

        self.render_cart_items()
        if self.alternative_rows:
            self.display_searched_alternatives()

# === Search Results Modal Class, displays search results in a modal overlay, called by SearchOverlayEngine ===
class SearchResultsModal:
    def __init__(self, canvas):
        self.canvas = canvas
        self.visible = False
        self.modal_elements = []
        self.list_frame = None
        self.window_id = None
        self.expanded_states = {}
        self.current_results = []

        self.last_search_query = ""
        self.sort_criterion = tk.StringVar(value="Relevance")

    def show_modal(self, search_query):
        theme = THEMES[current_theme_name]
        self.dismiss_modal()
        self.visible = True
        self.expanded_states.clear()

        self.last_search_query = search_query.lower().strip()

        dim_overlay = self.canvas.create_rectangle(
            0, 0, 410, 710,
            fill="#1C1C1E", outline=""
        )

        card_bg = self.canvas.create_rectangle(
            15, 80, 395, 610,
            fill=theme["card_bg"], outline=theme["card_bg"], width=2
        )

        header_title = self.canvas.create_text(
            30, 105, text=f"Results for '{search_query}'",
            font=("Helvetica Neue", 15, "bold"), fill=theme["text"], anchor="w"
        )

        btn_close = self.canvas.create_text(
            380, 105, text="✕ Close",
            font=("Helvetica Neue", 11, "bold"), fill="#FF3B30", anchor="e"
        )

        lbl_sort = self.canvas.create_text(
            30, 138, text="Sort by:",
            font=("Helvetica Neue", 10, "bold"), fill=theme["accent"], anchor="w"
        )

        sort_options = [
            "Relevance",
            "Price: Low to High", "Price: High to Low",
            "Unit Price: Low to High", "Unit Price: High to Low",
            "Health Rating: High to Low", "Health Rating: Low to High"
        ]

        self.sort_dropdown = ttk.Combobox(
            self.canvas.master, textvariable=self.sort_criterion,
            values=sort_options, state="readonly", font=("Helvetica Neue", 9)
        )
        self.sort_dropdown.bind("<<ComboboxSelected>>", lambda e: self.apply_sorting_and_render())

        dropdown_window = self.canvas.create_window(230, 138, window=self.sort_dropdown, width=220, height=24)
        divider_line = self.canvas.create_line(25, 160, 385, 160, fill=theme["accent"], width=1)

        container_frame = tk.Frame(self.canvas.master, bg=theme["card_bg"])
        canvas_scroll = tk.Canvas(container_frame, bg=theme["card_bg"], highlightthickness=0)
        scrollbar = ttk.Scrollbar(container_frame, orient="vertical", command=canvas_scroll.yview)

        self.list_frame = tk.Frame(canvas_scroll, bg=theme["card_bg"])
        self.list_frame.bind("<Configure>", lambda e: canvas_scroll.configure(scrollregion=canvas_scroll.bbox("all")))

        canvas_scroll.create_window((0, 0), window=self.list_frame, anchor="nw")
        canvas_scroll.configure(yscrollcommand=scrollbar.set)

        canvas_scroll.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.window_id = self.canvas.create_window(205, 385, window=container_frame, width=360, height=420)

        self.modal_elements.extend([dim_overlay, card_bg, header_title, btn_close, lbl_sort, dropdown_window, divider_line, self.window_id])

        self.canvas.tag_bind(btn_close, "<Button-1>", lambda e: self.dismiss_modal())
        self.canvas.tag_bind(dim_overlay, "<Button-1>", lambda e: self.dismiss_modal())

        self.perform_database_search(search_query)
        self.apply_sorting_and_render()
        self.lift_modal_stack()

    def perform_database_search(self, query):
        q = query.lower().strip()
        if not q:
            self.current_results = GROCERY_DATABASE
            return

        query_tokens = q.split()
        matches = []

        for item in GROCERY_DATABASE:
            name = item['name'].lower()
            variant = item['variant'].lower()
            full_str = f"{name} {variant}"
            item_id = item['id'].lower().replace('_', ' ')

            if all(token in full_str or token in item_id for token in query_tokens):
                matches.append((1, item))
                continue

            item_words = full_str.split()
            fuzzy_match = False

            for token in query_tokens:
                close = difflib.get_close_matches(token, item_words, n=1, cutoff=0.7)
                if close:
                    fuzzy_match = True
                    break

            if fuzzy_match:
                matches.append((2, item))

        matches.sort(key=lambda x: x[0])

        self.current_results = [item for priority, item in matches]

    def apply_sorting_and_render(self):
        if not self.list_frame:
            return
        for child in self.list_frame.winfo_children():
            child.destroy()

        criterion = self.sort_criterion.get()
        theme = THEMES[current_theme_name]

        def get_cheapest_store(item):
            return min(item["stores"], key=lambda x: x["price"])

        def get_cheapest_unit_store(item):
            return min(item["stores"], key=lambda x: x["unit_price"])

        def calculate_relevance_score(item):
            full_title = f"{item['name']} {item['variant']}".lower()

            base_ratio = difflib.SequenceMatcher(None, self.last_search_query, full_title).ratio()

            if self.last_search_query in full_title:
                return base_ratio + 10.0

            return base_ratio

        sorted_items = list(self.current_results)

        if criterion == "Relevance":
            sorted_items.sort(key=calculate_relevance_score, reverse=True)
        elif criterion == "Price: Low to High":
            sorted_items.sort(key=lambda x: get_cheapest_store(x)["price"])
        elif criterion == "Price: High to Low":
            sorted_items.sort(key=lambda x: get_cheapest_store(x)["price"], reverse=True)
        elif criterion == "Unit Price: Low to High":
            sorted_items.sort(key=lambda x: get_cheapest_unit_store(x)["unit_price"])
        elif criterion == "Unit Price: High to Low":
            sorted_items.sort(key=lambda x: get_cheapest_unit_store(x)["unit_price"], reverse=True)
        elif criterion == "Health Rating: High to Low":
            sorted_items.sort(key=lambda x: x["health_rating"], reverse=True)
        elif criterion == "Health Rating: Low to High":
            sorted_items.sort(key=lambda x: x["health_rating"])

        self.render_search_results_list(sorted_items, theme)

    def add_to_cart_action(self, item_payload, store_data):
        global USER_CART

        product_name = item_payload.get("name", "Unknown Item")
        variant = item_payload.get("variant", "Standard")
        health_score = item_payload.get("health_rating", 0.0)

        stars = "⭐" * int(health_score) + ("✨" if health_score % 1 != 0 else "")
        raw_description_label = f"Rating: {stars} ({health_score}/5.0) | Variant: {variant}"

        raw_nutriments = item_payload.get("nutriments", {})
        nutrition_payload = {
            "energy_kj": float(raw_nutriments.get("energy_kj", 0.0)),
            "fat_g": float(raw_nutriments.get("fat_g", 0.0)),
            "saturated_fat_g": float(raw_nutriments.get("saturated_fat_g", 0.0)),
            "sugars_g": float(raw_nutriments.get("sugars_g", 0.0)),
            "proteins_g": float(raw_nutriments.get("proteins_g", 0.0)),
            "salt_g": float(raw_nutriments.get("salt_g", 0.0))
        }

        USER_CART.append({
            "name": f"{product_name} ({store_data['store']})",
            "store": store_data["store"],
            "price": float(store_data["price"]),
            "description_label": raw_description_label,
            "nutriments": nutrition_payload
        })

        if 'dashboard_engine' in globals():
            reformatted_rows = []
            for cart_element in USER_CART[-3:]:
                reformatted_rows.append({
                    "name": cart_element["name"],
                    "price": f"${cart_element['price']:.2f}",
                    "desc": cart_element["description_label"].split("|")
                })
            globals()['dashboard_engine'].render_cart_items()

        if 'comparison_dashboard' in globals():
            globals()['comparison_dashboard'].render_cart_items()

        self.dismiss_modal()

    def render_search_results_list(self, sorted_items, theme):
        for idx, item in enumerate(sorted_items):
            item_card = tk.Frame(self.list_frame, bg=theme["bg"], bd=1, relief="solid")
            item_card.pack(fill="x", expand=True, pady=6, padx=4)

            t_label = tk.Label(item_card, text=f"{item['name']} ({item['variant']})", font=("Helvetica Neue", 11, "bold"), fg=theme["text"], bg=theme["bg"], anchor="w", justify="left")
            t_label.pack(fill="x", padx=6, pady=4)

            stars = "⭐" * int(item["health_rating"]) + ("✨" if item["health_rating"] % 1 != 0 else "")
            h_label = tk.Label(item_card, text=f"Health Rating: {stars} ({item['health_rating']}/5.0)", font=("Helvetica Neue", 9), fg=theme["accent"], bg=theme["bg"], anchor="w")
            h_label.pack(fill="x", padx=6)

            stores_sorted = sorted(item["stores"], key=lambda x: x["price"])
            cheapest = stores_sorted[0]

            cheap_frame = tk.Frame(item_card, bg=theme["bg"])
            cheap_frame.pack(fill="x", pady=2, padx=6)

            store_tag = tk.Label(cheap_frame, text=f" {cheapest['store']} ", font=("Helvetica Neue", 9, "bold"), fg="#FFFFFF", bg="#34C759", bd=0)
            store_tag.pack(side="left")

            price_txt = f" ${cheapest['price']:.2f} (${cheapest['unit_price']:.2f} / {cheapest['unit']})"
            price_lbl = tk.Label(cheap_frame, text=price_txt, font=("Helvetica Neue", 10, "bold"), fg=theme["text"], bg=theme["bg"])
            price_lbl.pack(side="left")

            btn_add_cheap = tk.Button(
                cheap_frame, text="+ Add", font=("Helvetica Neue", 8, "bold"), fg=theme["text"], bg=theme["bg"], bd=0, padx=6, activebackground=theme["bg"],
                command=lambda target_item=item, vendor=cheapest: self.add_to_cart_action(target_item, vendor)
            )
            btn_add_cheap.pack(side="right", padx=2)

            badge_lbl = tk.Label(cheap_frame, text=" [Cheapest Displayed]", font=("Helvetica Neue", 8, "italic"), fg="#007AFF", bg=theme["bg"])
            badge_lbl.pack(side="left")

            if len(stores_sorted) > 1:
                item_id = item["id"]
                is_expanded = self.expanded_states.get(item_id, False)
                toggle_btn = tk.Button(
                    item_card, text=f"{'▲ Hide' if is_expanded else '▼ Compare'} {len(stores_sorted)-1} other store options", font=("Helvetica Neue", 8, "bold"), fg="#007AFF", bg=theme["bg"], bd=0, activebackground=theme["bg"],
                    command=lambda i=item_id: self.toggle_store_accordion(i)
                )
                toggle_btn.pack(anchor="w", pady=2, padx=6)

                if is_expanded:
                    other_stores_frame = tk.Frame(item_card, bg=theme["bg"])
                    other_stores_frame.pack(fill="x", padx=10, pady=2)

                    for ot in stores_sorted[1:]:
                        o_line = tk.Label(other_stores_frame, text=f"• {ot['store']}: ${ot['price']:.2f} (${ot['unit_price']:.2f} / {ot['unit']})", font=("Helvetica Neue", 9), fg=theme["text"], bg=theme["bg"], anchor="w")
                        o_line.pack(fill="x")

                        btn_add_ot = tk.Button(
                            o_line, text="+ Add", font=("Helvetica Neue", 7, "bold"), fg="#007AFF", bg=theme["bg"], bd=0,
                            command=lambda target_item=item, vendor=ot: self.add_to_cart_action(target_item, vendor)
                        )
                        btn_add_ot.pack(side="right", padx=4)

    def toggle_store_accordion(self, item_id):
        self.expanded_states[item_id] = not self.expanded_states.get(item_id, False)

        self.canvas.after(10, self.apply_sorting_and_render)

    def update_colors(self):
        if self.visible:
            self.apply_sorting_and_render()

    def dismiss_modal(self):
        if hasattr(self, 'modal_elements'):
            for element_id in self.modal_elements:
                self.canvas.delete(element_id)
            self.modal_elements.clear()

        self.visible = False
        self.list_frame = None

    def lift_modal_stack(self):
        if hasattr(self, 'modal_elements'):
            for eid in self.modal_elements:
                self.canvas.lift(eid)

# === Search Overlay Engine Class, manages the search interface overlay on the main page, calls SearchResultsModal ===
class SearchOverlayEngine:
    def __init__(self, canvas, start_y=395):
        self.canvas = canvas
        self.start_y = start_y
        self.left_x = 20
        self.width = 370
        self.right_x = self.left_x + self.width
        self.center_x = (self.left_x + self.right_x) / 2
        self.radius = 16

        self.overlay_elements = []
        self.result_row_elements = []
        self.entry_widget = None

    def summon_search_interface(self):
        theme = THEMES[current_theme_name]
        self.dismiss_search_interface()

        x1, y1 = self.left_x, self.start_y
        x2, y2 = self.right_x, self.start_y + 190
        r = self.radius
        points = [
            x1+r, y1,   x2-r, y1,   x2, y1,
            x2, y1+r,   x2, y2-r,   x2, y2,
            x2-r, y2,   x1+r, y2,   x1, y2,
            x1, y2-r,   x1, y1+r,   x1, y1
        ]

        card_bg = self.canvas.create_polygon(
            points, fill=theme["card_bg"], outline=theme["card_bg"], width=1, smooth=True, splinesteps=32
        )

        lbl_title = self.canvas.create_text(
            self.left_x + 20, self.start_y + 20,
            text="Global Grocery & Supermarket Search", font=("Helvetica Neue", 12, "bold"), fill=theme["text"], anchor="w"
        )
        btn_close = self.canvas.create_text(
            self.right_x - 20, self.start_y + 20,
            text="Close X", font=("Helvetica Neue", 10, "bold"), fill="#FF3B30", anchor="e"
        )

        self.entry_widget = tk.Entry(
            self.canvas.master, font=("Helvetica Neue", 11),
            bg=theme["bg"], fg=theme["text"], bd=0, highlightthickness=1, highlightcolor=theme["accent"]
        )
        window_input = self.canvas.create_window(
            self.center_x - 32, self.start_y + 55, window=self.entry_widget, width=235, height=28
        )

        btn_go_bg = self.canvas.create_oval(
            self.right_x - 45, self.start_y + 41, self.right_x - 15, self.start_y + 69,
            fill=theme["btn_bg"], outline=""
        )
        txt_go_icon = self.canvas.create_text(
            self.right_x - 30, self.start_y + 55,
            text="➔", font=("Helvetica Neue", 10, "bold"), fill=theme["btn_txt"], anchor="center"
        )

        btn_cam_bg = self.canvas.create_oval(
            self.right_x - 90, self.start_y + 41, self.right_x - 60, self.start_y + 69,
            fill="#007AFF" if theme != "invert" else theme["blue_txt"], outline=""
        )
        txt_cam_icon = self.canvas.create_text(
            self.right_x - 77, self.start_y + 55,
            text="📷", font=("Helvetica Neue", 11), fill="#FFFFFF", anchor="center"
        )

        self.overlay_elements.extend([card_bg, lbl_title, btn_close, window_input, btn_go_bg, txt_go_icon, btn_cam_bg, txt_cam_icon])

        self.canvas.tag_bind(btn_close, "<Button-1>", lambda e: self.dismiss_search_interface())
        self.canvas.tag_bind(btn_go_bg, "<Button-1>", self.execute_text_matching_search)
        self.canvas.tag_bind(txt_go_icon, "<Button-1>", self.execute_text_matching_search)
        self.entry_widget.bind("<Return>", self.execute_text_matching_search)

        def handle_camera_activation_click(event):
            self.dismiss_search_interface()
            hardware_scanner.trigger_scan()

        self.canvas.tag_bind(btn_cam_bg, "<Button-1>", handle_camera_activation_click)
        self.canvas.tag_bind(txt_cam_icon, "<Button-1>", handle_camera_activation_click)

        self.entry_widget.focus_set()
        self.lift_overlay_stack()

    def execute_text_matching_search(self, event=None):
        if not self.entry_widget:
            return
        user_raw_query = self.entry_widget.get().strip()
        if len(user_raw_query) < 1:
            return

        self.dismiss_search_interface()
        search_popup_modal.show_modal(user_raw_query)

    def dismiss_search_interface(self):
        for element_id in self.overlay_elements:
            self.canvas.delete(element_id)
        self.clear_result_row_elements()
        self.overlay_elements.clear()
        self.entry_widget = None

    def clear_result_row_elements(self):
        for element_id in self.result_row_elements:
            self.canvas.delete(element_id)
        self.result_row_elements.clear()

    def lift_overlay_stack(self):
        for eid in self.overlay_elements: self.canvas.lift(eid)
        for eid in self.result_row_elements: self.canvas.lift(eid)

# === Map Page Engine Class, manages the map page UI and interactions, including launching Google Maps for nearby grocers ===
class MapPageEngine:
    def __init__(self, canvas):
        self.canvas = canvas
        self.map_ui_elements = []
        self.current_lat = None
        self.current_lon = None
        self._build_ui()

    def _build_ui(self):
        theme = THEMES[current_theme_name]
        self.title_id = self.canvas.create_text(25, 120, text="Nearby Grocers", font=("Helvetica Neue", 22, "bold"), fill=theme["text"], anchor="nw", state="hidden")
        self.subtitle_id = self.canvas.create_text(25, 160, text="Opens Google Maps directly for Aldi, IGA,\nWoolworths & Coles centered on your area.", font=("Helvetica Neue", 11), fill=theme["accent"], anchor="nw", state="hidden")

        self.btn_gmaps_bg = self.canvas.create_line(45, 250, 365, 250, width=44, fill="#007AFF", capstyle="round", state="hidden")
        self.btn_gmaps_txt = self.canvas.create_text(205, 250, text="🗺 Launch Google Maps", font=("Helvetica Neue", 12, "bold"), fill="#FFFFFF", anchor="center", state="hidden")

        self.map_ui_elements.extend([self.title_id, self.subtitle_id, self.btn_gmaps_bg, self.btn_gmaps_txt])

        self.canvas.tag_bind(self.btn_gmaps_bg, "<Button-1>", lambda e: self.open_google_maps_grocers())
        self.canvas.tag_bind(self.btn_gmaps_txt, "<Button-1>", lambda e: self.open_google_maps_grocers())

    def open_google_maps_grocers(self):
        def launch():
            query_str = quote("Aldi OR Coles OR Woolworths OR IGA grocers")
            url = f"https://www.google.com/maps/search/{query_str}"
            webbrowser.open(url)

        threading.Thread(target=launch, daemon=True).start()

    def update_colors(self):
        theme = THEMES[current_theme_name]
        try:
            self.canvas.itemconfig(self.title_id, fill=theme["text"])
            self.canvas.itemconfig(self.subtitle_id, fill=theme["accent"])
        except Exception:
            pass

# === Settings Page Engine Class, manages the settings page UI and interactions, including persistent theme and sorting preferences ===
class SettingsPageEngine:
    def __init__(self, canvas, start_y=110):
        self.canvas = canvas
        self.start_y = start_y

        self.left_x = 25
        self.right_x = 385
        self.center_x = (self.left_x + self.right_x) / 2
        self.radius = 16

        self.settings_ui_elements = []
        self.sub_overlay_elements = []
        self.embedded_widgets = []

        self.w_appear_id = None
        self.w_sort_id = None

        self.appearance_var = tk.StringVar(value="Light Mode")
        self.sorting_var = tk.StringVar(value="Relevance")

        self.build_settings_menu_interface()

    def build_settings_menu_interface(self):
        theme = THEMES[current_theme_name]
        self.clear_entire_interface()

        title_lbl = self.canvas.create_text(
            self.left_x, self.start_y,
            text="Settings", font=("Helvetica Neue", 26, "bold"), fill=theme["text"], anchor="nw", state="hidden"
        )
        self.settings_ui_elements.append(title_lbl)

        lbl_group1 = self.canvas.create_text(
            self.left_x + 5, self.start_y + 45,
            text="SYSTEM CONFIGURATIONS", font=("Helvetica Neue", 9, "bold"), fill=theme["accent"], anchor="w", state="hidden"
        )
        self.settings_ui_elements.append(lbl_group1)

        x1, y1 = self.left_x, self.start_y + 55
        x2, y2 = self.right_x, self.start_y + 215
        r = self.radius
        points1 = [
            x1+r, y1,   x2-r, y1,   x2, y1,
            x2, y1+r,   x2, y2-r,   x2, y2,
            x2-r, y2,   x1+r, y2,   x1, y2,
            x1, y2-r,   x1, y1+r,   x1, y1
        ]

        self.card1 = self.canvas.create_polygon(
            points1, fill=theme["card_bg"], outline=theme["card_bg"], width=1, smooth=True, splinesteps=32, state="hidden"
        )
        self.settings_ui_elements.append(self.card1)

        lbl_appear = self.canvas.create_text(self.left_x + 15, self.start_y + 85, text="Default Appearance", font=("Helvetica Neue", 11, "bold"), fill=theme["text"], anchor="w", state="hidden")
        self.settings_ui_elements.append(lbl_appear)

        appear_options = ["Light Mode", "Dark Mode", "Pro-Duo (Colorblind)", "Inverted Contrast"]
        self.sync_appearance_string_variable()

        cb_appear = ttk.Combobox(self.canvas.master, textvariable=self.appearance_var, values=appear_options, state="readonly", font=("Helvetica Neue", 9))
        cb_appear.bind("<<ComboboxSelected>>", self.execute_live_theme_switch)

        self.w_appear_id = self.canvas.create_window(self.right_x - 115, self.start_y + 85, window=cb_appear, width=150, height=22, state="hidden")
        self.settings_ui_elements.append(self.w_appear_id)

        self.build_list_divider_line(self.start_y + 105)

        lbl_sort = self.canvas.create_text(self.left_x + 15, self.start_y + 135, text="Default Sorting", font=("Helvetica Neue", 11, "bold"), fill=theme["text"], anchor="w", state="hidden")
        self.settings_ui_elements.append(lbl_sort)

        sort_options = ["Relevance", "Price: Low to High", "Price: High to Low", "Health Rating: High to Low"]
        cb_sort = ttk.Combobox(self.canvas.master, textvariable=self.sorting_var, values=sort_options, state="readonly", font=("Helvetica Neue", 9))
        cb_sort.bind("<<ComboboxSelected>>", self.execute_global_sort_preference_update)

        self.w_sort_id = self.canvas.create_window(self.right_x - 115, self.start_y + 135, window=cb_sort, width=150, height=22, state="hidden")
        self.settings_ui_elements.append(self.w_sort_id)

        self.build_list_divider_line(self.start_y + 155)

        # Handler for launching system notification settings based on the OS
        def launch_hardware_system_notification_settings():
            try:
                if sys.platform.startswith("darwin"):
                    applescript_command = 'tell application "System Settings" to activate\nopen location "x-apple.systempreferences:com.apple.Notifications-Settings.extension"'
                    subprocess.Popen(['osascript', '-e', applescript_command])
                elif sys.platform.startswith("win32"):
                    subprocess.Popen(['start', 'ms-settings:notifications'], shell=True)
            except:
                pass

        self.build_navigable_action_row("Notification Settings", self.start_y + 185, lambda: launch_hardware_system_notification_settings())

        lbl_group2 = self.canvas.create_text(
            self.left_x + 5, self.start_y + 240,
            text="LEGAL DISCLOSURES & REGULATORY INFO", font=("Helvetica Neue", 9, "bold"), fill=theme["accent"], anchor="w", state="hidden"
        )
        self.settings_ui_elements.append(lbl_group2)

        y1_b, y2_b = self.start_y + 250, self.start_y + 370
        points2 = [
            x1+r, y1_b,   x2-r, y1_b,   x2, y1_b,
            x2, y1_b+r,   x2, y2_b-r,   x2, y2_b,
            x2-r, y2_b,   x1+r, y2_b,   x1, y2_b,
            x1, y2_b-r,   x1, y1_b+r,   x1, y1_b
        ]

        card2 = self.canvas.create_polygon(
            points2, fill=theme["card_bg"], outline=theme["card_bg"], width=1, smooth=True, splinesteps=32, state="hidden"
        )
        self.settings_ui_elements.append(card2)

        self.build_navigable_action_row("Privacy Policy Disclosure", self.start_y + 280, lambda: self.summon_disclosure_modal("pp"))
        self.build_list_divider_line(self.start_y + 310)

        self.build_navigable_action_row("Terms of Service Agreement", self.start_y + 340, lambda: self.summon_disclosure_modal("tos"))

    def sync_appearance_string_variable(self):
        mapping = {
            "light": "Light Mode",
            "dark": "Dark Mode",
            "pro-duo-triteranopia": "Pro-Duo (Colorblind)",
            "inverted": "Inverted Contrast"
        }
        set_theme_name = SESSION_DATA["preferences"]["default_theme"]
        self.appearance_var.set(mapping.get(set_theme_name, "Light Mode"))

    def execute_live_theme_switch(self, event=None):
        global current_theme_name, SESSION_DATA
        choice = self.appearance_var.get()

        mapping = {
            "Light Mode": "light", "Dark Mode": "dark",
            "Pro-Duo (Colorblind)": "pro-duo-triteranopia", "Inverted Contrast": "inverted"
        }

        new_theme = mapping.get(choice, "light")
        if new_theme != current_theme_name:
            current_theme_name = new_theme

            SESSION_DATA["preferences"]["default_theme"] = new_theme

            save_user_to_database(
                display_name=SESSION_DATA.get("display_name", "Guest Account"),
                passcode=SESSION_DATA.get("passcode", ""),
                preferences_dict=SESSION_DATA["preferences"]
            )

            update_system_wide_themes()
            self.sync_appearance_string_variable()

    def execute_global_sort_preference_update(self, event=None):
        global SESSION_DATA
        choice = self.sorting_var.get()

        if 'search_popup_modal' in globals():
            globals()['search_popup_modal'].sort_criterion.set(choice)

        SESSION_DATA["preferences"]["default_sort"] = choice
        save_user_to_database(
            display_name=SESSION_DATA.get("display_name", "Guest Account"),
            passcode=SESSION_DATA.get("passcode", ""),
            preferences_dict=SESSION_DATA["preferences"]
        )

    def build_navigable_action_row(self, row_label_text, y_coordinate, programmatic_action_callback):
        theme = THEMES[current_theme_name]

        txt_node = self.canvas.create_text(self.left_x + 15, y_coordinate, text=row_label_text, font=("Helvetica Neue", 11, "bold"), fill=theme["text"], anchor="w", state="hidden")
        chevron_node = self.canvas.create_text(self.right_x - 20, y_coordinate, text="〉", font=("Helvetica Neue", 10, "bold"), fill=theme["accent"], anchor="center", state="hidden")
        hit_box = self.canvas.create_rectangle(self.left_x, y_coordinate - 14, self.right_x, y_coordinate + 14, fill="", outline="", state="hidden")

        self.settings_ui_elements.append(txt_node)
        self.settings_ui_elements.append(chevron_node)
        self.settings_ui_elements.append(hit_box)

        for tracking_id in (txt_node, chevron_node, hit_box):
            self.canvas.tag_bind(tracking_id, "<Button-1>", lambda e: programmatic_action_callback())

    def build_list_divider_line(self, y_coordinate):
        theme = THEMES[current_theme_name]
        div_line = self.canvas.create_line(self.left_x + 15, y_coordinate, self.right_x - 15, y_coordinate, fill=theme["accent"], width=1, state="hidden")
        self.settings_ui_elements.append(div_line)

    def summon_disclosure_modal(self, type: str):
        theme = THEMES[current_theme_name]
        self.dismiss_disclosure_modal()

        if self.w_appear_id is not None:
            self.canvas.itemconfig(self.w_appear_id, state="hidden")
        if self.w_sort_id is not None:
            self.canvas.itemconfig(self.w_sort_id, state="hidden")

        if type == "pp":
            popup_title_text = "Privacy Policy Disclosure"
            paragraph_body_text = (
                "Sift User Privacy Protection Architecture\n"
                "Last Updated: August 2026\n\n"
                "1. Overview:\n"
                "Sift is a locally operated grocery analysis application. This Privacy Policy explains what information Sift collects, how it is used, and the rights available to you as a user. Sift is designed with data minimisation as a core principle. We collect only what is strictly necessary for the application to function.\n"
                "\n"
                "2. Information We Collect:\n"
                "> Information you provide:\n"
                "Sift stores a username and password locally on your device to support account sessions. No email address, phone number, or government-issued identification is required or collected.\n\n"
                "> Barcode scan history:\n"
                "Products you scan are stored locally on your device. This history is used solely to provide you with your personal scan history and product preferences within the application.\n\n"
                "> Third-party product data:\n"
                "When you scan a barcode, Sift transmits the barcode number to the Open Food Facts API to retrieve product information. This transmission contains only the barcode value — no personal identifiers, account information, or device data is included. Open Food Facts is an independent, non-profit open database. Their privacy policy can be found at world.openfoodfacts.org.\n"
                "\n"
                "3. How We Use Your Information:\n"
                "Sift uses locally stored data exclusively to:\n"
                "- Maintain your account session between uses\n"
                "- Display your scan history\n"
                "- Provide personalised product comparisons and recommendations\n\n"
                "We do not use your data for advertising, profiling, or any commercial purpose.\n"
                "\n"
                "4. Data Storage and Security:\n"
                "All user data is stored locally on your device in a structured file format. Sift does not operate remote servers, cloud databases, or centralised data infrastructure. Your data does not leave your device except for the barcode values transmitted to Open Food Facts as described above.\n"
                "We implement reasonable local security practices; however, we recommend keeping your device secure and not sharing your Sift account credentials with others.\n"
                "\n"
                "5. Children's Privacy:\n"
                "Sift is not directed at children under the age of 13. We do not knowingly collect personal information from children. If you believe a child has used Sift and stored personal data without appropriate consent, please contact us so the data can be removed.\n"
                "\n"
                "7. Changes to This Policy:\n"
                "We may update this Privacy Policy from time to time. Significant changes will be communicated within the application. Continued use of Sift following any changes constitutes acceptance of the updated policy."
            )
        elif type == "tos":
            popup_title_text = "Terms of Service Agreement"
            paragraph_body_text = (
                "Sift Application Usage Terms & Conditions\n"
                "Last Updated: August 2026\n\n"
                "1. Acceptance of Terms:\n"
                "By initializing and interacting with the Sift software application, you acknowledge and agree to remain bound by these localized operational terms and design constraints. If you do not accept these parameters, do not run the application.\n\n"
                "2. Permitted Application Scope & Usage:\n"
                "Sift provides an informative, experimental interface prototype designed exclusively for side-by-side sustainable grocery analysis. All outputs, product evaluations, and data metrics generated by the software are for educational simulation testing purposes only and must never be leveraged as absolute financial, legal, medical, or clinical logistics advice.\n\n"
                "3. Remote API Sourcing & Data Integrity:\n"
                "Environmental and nutritional attributes (including life-cycle EcoScore Grades, carbon estimates, NutriScore vectors, and NOVA processing tiers) are fetched live from remote open-source servers via Open Food Facts web API endpoints. Sift acts purely as a transparent data pipeline client. We make no binding legal claims regarding external product database correctness.\n\n"
                "4. Consumer Law & Greenwashing Regulations:\n"
                "To satisfy regulatory definitions under Australian Consumer Law (Competition and Consumer Act 2010), all eco-label profiles display completely raw, unedited parameters directly from source records. This objective data routing framework entirely eliminates corporate advertisement priority biases, neutralizing greenwashing manipulation risks to comply fully with active ACCC retail guidelines.\n\n"
                "5. Unit Pricing Verification Laws:\n"
                "Product alternative comparison panels sort and display multi-location grocery listings using standardized unit parameters matching the Competition and Consumer Regulations Act 2010. This guarantees objective, side-by-side comparison visibility and consumer cost transparency.\n\n"
                "6. System Modification & Termination:\n"
                "Developers Patrick and Safin reserve the right to refine code loops, optimize multi-page visibility routing layers, or suspend dynamic API transaction data pipelines at any stage to preserve platform execution security and local performance speeds without notice."
            )

        shield = self.canvas.create_rectangle(0, 0, 410, 710, fill="#1C1C1E", outline="", state="normal")
        modal_bg = self.canvas.create_rectangle(20, 100, 390, 600, fill=theme["card_bg"], outline=theme["card_bg"], width=1, state="normal")
        modal_title = self.canvas.create_text(40, 130, text=popup_title_text, font=("Helvetica Neue", 16, "bold"), fill=theme["text"], anchor="w", state="normal")
        btn_close = self.canvas.create_text(370, 130, text="✕ Close", font=("Helvetica Neue", 10, "bold"), fill="#FF3B30", anchor="e", state="normal")

        text_container_frame = tk.Frame(self.canvas.master, bg=theme["card_bg"])

        scrollable_text_box = tk.Text(text_container_frame, wrap="word", font=("Helvetica Neue", 10),bg=theme["card_bg"], fg=theme["text"], bd=0, highlightthickness=0)
        scrollbar_track = ttk.Scrollbar(text_container_frame, orient="vertical", command=scrollable_text_box.yview)
        scrollable_text_box.configure(yscrollcommand=scrollbar_track.set)
        scrollbar_track.pack(side="right", fill="y")
        scrollable_text_box.pack(side="left", fill="both", expand=True)
        scrollable_text_box.insert("1.0", paragraph_body_text)
        scrollable_text_box.configure(state="disabled")

        modal_window_body_id = self.canvas.create_window(205, 375, window=text_container_frame, width=330, height=400, state="normal")

        for eid in (shield, modal_bg, modal_title, btn_close, modal_window_body_id):
            self.sub_overlay_elements.append(eid)

        self.canvas.tag_bind(btn_close, "<Button-1>", lambda e: self.dismiss_disclosure_modal())
        self.lift_settings_modal_stack()

    def dismiss_disclosure_modal(self):
        for element_id in self.sub_overlay_elements:
            self.canvas.delete(element_id)
        self.sub_overlay_elements.clear()

        if self.canvas.itemcget(self.card1, "state") != "hidden":
            if self.w_appear_id is not None:
                self.canvas.itemconfig(self.w_appear_id, state="normal")
            if self.w_sort_id is not None:
                self.canvas.itemconfig(self.w_sort_id, state="normal")

    def lift_settings_modal_stack(self):
        for eid in self.sub_overlay_elements:
            self.canvas.lift(eid)

    def set_visibility(self, state_string):
        for element_id in self.settings_ui_elements:
            self.canvas.itemconfig(element_id, state=state_string)
        for element_id in self.sub_overlay_elements:
            self.canvas.itemconfig(element_id, state=state_string)

        if state_string == "hidden":
            for widget in self.embedded_widgets:
                widget.place_forget()
            self.dismiss_disclosure_modal()
        else:
            self.build_settings_menu_interface()

    def clear_entire_interface(self):
        for element_id in self.settings_ui_elements:
            self.canvas.delete(element_id)
        self.settings_ui_elements.clear()
        self.embedded_widgets.clear()

    def update_colors(self):
        if not hasattr(self, 'settings_ui_elements') or not self.settings_ui_elements:
            return

        theme = THEMES[current_theme_name]
        self.sync_appearance_string_variable()

        for eid in self.settings_ui_elements:
            try:
                element_type = self.canvas.type(eid)

                if element_type == "text":
                    current_txt_val = self.canvas.itemcget(eid, "text")
                    if current_txt_val in ["SYSTEM CONFIGURATIONS", "LEGAL DISCLOSURES & REGULATORY INFO", "〉"]:
                        self.canvas.itemconfig(eid, fill=theme["accent"])
                    else:
                        self.canvas.itemconfig(eid, fill=theme["text"])

                elif element_type == "polygon":
                    self.canvas.itemconfig(eid, fill=theme["card_bg"], outline=theme["card_bg"])

                elif element_type == "line":
                    if self.canvas.itemcget(eid, "width") in ["1.0", "1", "1.00"]:
                        self.canvas.itemconfig(eid, fill=theme["accent"])

                elif element_type == "window":
                    pass

            except Exception:
                pass

# === Bottom Navigation Bar Class, manages the bottom navigation bar UI and interactions ===
class BottomNavigationBar:
    def __init__(self, canvas, center_x, center_y, on_page_changed_callback):
        self.canvas = canvas
        self.center_x = center_x
        self.center_y = center_y
        self.on_page_changed = on_page_changed_callback

        self.current_indicator_x = center_x - 70
        self.target_indicator_x = center_x - 70
        self.is_animating = False

        self.bar_bg = canvas.create_line(
            center_x - 100, center_y, center_x + 100, center_y,
            width=44, fill="#FFFFFF", capstyle="round"
        )

        self.indicator = canvas.create_line(
            self.current_indicator_x - 25, center_y, self.current_indicator_x + 25, center_y,
            width=36, fill="#E5E5EA", capstyle="round"
        )

        self.tabs_metadata = [
            {"name": "Main", "x": center_x - 70},
            {"name": "Map", "x": center_x},
            {"name": "Settings", "x": center_x + 70}
        ]

        self.tab_elements = []
        self.icon_light_cache = {}
        self.icon_dark_cache = {}
        self.load_and_process_assets()
        self.build_navigation_items()

        # Activating bottom search icon button
        self.btn_search_bg = canvas.create_oval(
            center_x + 135, center_y - 22, center_x + 155 + 24, center_y + 22,
            fill="#FFFFFF", outline=""
        )
        self.txt_search_icon = canvas.create_text(
            center_x + 155 + 2, center_y,
            text="🔍", font=("Helvetica Neue", 12), anchor="center"
        )

        canvas.tag_bind(self.btn_search_bg, "<Button-1>", lambda e: search_overlay.summon_search_interface())
        canvas.tag_bind(self.txt_search_icon, "<Button-1>", lambda e: search_overlay.summon_search_interface())

    def load_and_process_assets(self):
        tab_url_map = {
            "Main": "tabMain",
            "Map": "tabMap",
            "Settings": "tabSettings"
        }

        for tab in self.tabs_metadata:
            name = tab["name"]
            url_key = tab_url_map.get(name, None)
            url_string = IMAGE_URLS.get(url_key, None)

            try:
                response = requests.get(url_string, timeout=4)
                img_pil_orig = Image.open(io.BytesIO(response.content)).convert("RGBA").resize((20, 20), Image.Resampling.LANCZOS)
                self.icon_light_cache[name] = ImageTk.PhotoImage(img_pil_orig)

                r, g, b, a = img_pil_orig.split()
                r_inv = r.point(lambda p: 255 - p)
                g_inv = g.point(lambda p: 255 - p)
                b_inv = b.point(lambda p: 255 - p)

                img_inverted_pil = Image.merge("RGBA", (r_inv, g_inv, b_inv, a))
                self.icon_dark_cache[name] = ImageTk.PhotoImage(img_inverted_pil)
            except Exception as e:
                blank = ImageTk.PhotoImage(Image.new("RGBA", (1, 1), (0, 0, 0, 0)))
                self.icon_light_cache[name] = blank
                self.icon_dark_cache[name] = blank

    def build_navigation_items(self):
        theme = THEMES[current_theme_name]
        for idx, tab in enumerate(self.tabs_metadata):
            name = tab["name"]

            i_id = self.canvas.create_image(
                tab["x"], self.center_y - 6,
                image=self.icon_light_cache[name], anchor="center"
            )
            t_id = self.canvas.create_text(
                tab["x"], self.center_y + 11,
                text=name, font=("Helvetica Neue", 8, "bold"), anchor="center"
            )

            initial_color = "#007AFF" if idx == 0 else theme["text"]
            self.canvas.itemconfig(t_id, fill=initial_color)

            self.tab_elements.append({"text_id": t_id, "image_id": i_id})
            self.setup_tab_click_events(i_id, t_id, idx)

    def setup_tab_click_events(self, image_id, text_id, index):
        def on_click(event):
            self.switch_to_tab(index)
        self.canvas.tag_bind(image_id, "<Button-1>", on_click)
        self.canvas.tag_bind(text_id, "<Button-1>", on_click)

    def switch_to_tab(self, target_index):
        theme = THEMES[current_theme_name]
        self.target_indicator_x = self.tabs_metadata[target_index]["x"]

        for idx, element in enumerate(self.tab_elements):
            active_color = "#007AFF" if idx == target_index else theme["text"]
            self.canvas.itemconfig(element["text_id"], fill=active_color)

        if not self.is_animating:
            self.step_indicator_slide()

        self.on_page_changed(self.tabs_metadata[target_index]["name"])

    def step_indicator_slide(self):
        diff = self.target_indicator_x - self.current_indicator_x
        if abs(diff) < 1:
            self.current_indicator_x = self.target_indicator_x
            self.is_animating = False
        else:
            self.is_animating = True
            self.current_indicator_x += diff * 0.25
            self.canvas.after(16, self.step_indicator_slide)

        self.canvas.coords(
            self.indicator,
            self.current_indicator_x - 25, self.center_y,
            self.current_indicator_x + 25, self.center_y
        )
        self.lift_navigation_stack()

    def lift_navigation_stack(self):
        self.canvas.lift(self.bar_bg)
        self.canvas.lift(self.indicator)
        for element in self.tab_elements:
            self.canvas.lift(element["image_id"])
            self.canvas.lift(element["text_id"])

    def update_colors(self):
        theme = THEMES[current_theme_name]
        self.canvas.itemconfig(self.bar_bg, fill=theme["card_bg"])
        self.canvas.itemconfig(self.indicator, fill=theme["bg"])
        self.canvas.itemconfig(self.btn_search_bg, fill=theme["card_bg"])
        self.canvas.itemconfig(self.txt_search_icon, fill=theme["text"])

        use_inverted_assets = current_theme_name in ["dark", "inverted"]
        active_cache = self.icon_dark_cache if use_inverted_assets else self.icon_light_cache

        for idx, element in enumerate(self.tab_elements):
            name = self.tabs_metadata[idx]["name"]
            self.canvas.itemconfig(element["image_id"], image=active_cache[name])
            if self.tabs_metadata[idx]["x"] != self.target_indicator_x:
                self.canvas.itemconfig(element["text_id"], fill=theme["text"])

# === WINDOW INITIALIZATION ===
root = tk.Tk()
root.title("Sift")
root.geometry("450x750")
root.configure(bg="#1C1C1E")

# === INITIALIZE PERSISTENT SETTINGS AND CONFIGURATIONS ===
saved_default_theme = SESSION_DATA["preferences"].get("default_theme", "light")
saved_default_sort = SESSION_DATA["preferences"].get("default_sort", "Relevance")
current_theme_name = saved_default_theme

# === APPLE UI AND PERSISTENT CONTENT ===
master_bg = tk.Canvas(root, width=410, height=710, bg="#1C1C1E", highlightthickness=0)
master_bg.place(x=20, y=20)
master_bg.bind("<Button-1>", handle_background_click)

draw_master_canvas(master_bg, width=410, height=710, radius=32, color="#F2F2F7")

txt_clock = master_bg.create_text(25, 12, text="00:00", font=("Helvetica Neue", 11, "bold"), fill="#000000", anchor="nw")
txt_battery = master_bg.create_text(385, 12, text="--%", font=("Helvetica Neue", 11, "bold"), fill="#000000", anchor="ne")

txt_logo = master_bg.create_text(25, 45, text="Sift", font=("Helvetica Neue", 32, "bold"), fill="#000000", anchor="nw")
sift_logo_path = IMAGE_URLS.get("siftLogo")
try:
    response = requests.get(sift_logo_path, timeout=4)
    img_pil_orig = Image.open(io.BytesIO(response.content)).convert("RGBA").resize((50, 50), Image.Resampling.LANCZOS)
    icon_light_cache = ImageTk.PhotoImage(img_pil_orig)

    r, g, b, a = img_pil_orig.split()
    r_inv = r.point(lambda p: 255 - p)
    g_inv = g.point(lambda p: 255 - p)
    b_inv = b.point(lambda p: 255 - p)

    img_inverted_pil = Image.merge("RGBA", (r_inv, g_inv, b_inv, a))
    icon_dark_cache = ImageTk.PhotoImage(img_inverted_pil)
    logo_image_id = master_bg.create_image(85, 40, image=icon_light_cache, anchor="nw")
except Exception as e:
    icon_light_cache = ImageTk.PhotoImage(Image.new("RGBA", (1, 1), (0, 0, 0, 0)))
    icon_dark_cache = icon_light_cache
    logo_image_id = master_bg.create_image(85, 40, image=icon_light_cache, anchor="nw")

PROFILE_BTN_CENTER_X = 345
btn_profile_bg = master_bg.create_oval(PROFILE_BTN_CENTER_X, 48, PROFILE_BTN_CENTER_X + 34, 48 + 34, width=1)
txt_profile_icon = master_bg.create_text((PROFILE_BTN_CENTER_X + PROFILE_BTN_CENTER_X + 34)/2, 64, text="≡", font=("Helvetica Neue", 18, "bold"), anchor="center")

THEMES_BTN_CENTER_X = 300
btn_theme_bg = master_bg.create_oval(THEMES_BTN_CENTER_X, 48, THEMES_BTN_CENTER_X + 34, 48 + 34, width=1)
img_theme_icon = master_bg.create_image((THEMES_BTN_CENTER_X + THEMES_BTN_CENTER_X + 34)/2, 65, image="", anchor="center")

# === MAIN PAGE CONFIGURATION WORKSPACE ===
compare_btn = AnimatedCapsuleButton(canvas=master_bg, x1=45, y1=310, x2=365, y2=310, fill_color="#000000", text="Compare Products", command=on_compare_trigger, base_width=40)

comparison_dashboard = ComparisonDashboard(master_bg, start_y=395)

dashboard_engine = comparison_dashboard

PAGE_MAIN_ELEMENTS.clear()
PAGE_MAIN_ELEMENTS.extend([compare_btn.line_id, compare_btn.text_id])
PAGE_MAIN_ELEMENTS.extend(comparison_dashboard.ui_elements)

# === MAP PAGE CONFIGURATION WORKSPACE ===
map_page = MapPageEngine(master_bg)
PAGE_MAP_ELEMENTS.clear()
PAGE_MAP_ELEMENTS.extend(map_page.map_ui_elements)

# === SETTINGS PAGE CONFIGURATION WORKSPACE ===
settings_page = SettingsPageEngine(master_bg)
PAGE_SETTINGS_ELEMENTS.clear()
PAGE_SETTINGS_ELEMENTS.extend(settings_page.settings_ui_elements)

# === INITIALIZE PERSISTENT ENGINE COMPONENTS ===
product_panel = SlideMenu(master_bg, width=410, height=710)
profile_menu = ProfileSlideMenu(master_bg, width=410, height=710)
theme_dropdown = HorizontalThemeDropdown(master_bg, anchor_x=290, anchor_y=65)
search_overlay = SearchOverlayEngine(master_bg, start_y=395)
search_popup_modal = SearchResultsModal(master_bg)
hardware_scanner = AdvancedCameraScanner(master_bg)
bottom_nav_bar = BottomNavigationBar(canvas=master_bg, center_x=185, center_y=640, on_page_changed_callback=on_system_page_route_changed)

# === INITIALIZE BINDINGS FOR INTERACTIVE ELEMENTS ===
master_bg.tag_bind(btn_theme_bg, "<Button-1>", lambda e: theme_dropdown.toggle())
master_bg.tag_bind(img_theme_icon, "<Button-1>", lambda e: theme_dropdown.toggle())
master_bg.tag_bind(btn_profile_bg, "<Button-1>", lambda e: profile_menu.toggle(open_panel=True))
master_bg.tag_bind(txt_profile_icon, "<Button-1>", lambda e: profile_menu.toggle(open_panel=True))

if 'search_popup_modal' in globals():
    search_popup_modal.sort_criterion.set(saved_default_sort)
if 'settings_page' in globals():
    settings_page.sorting_var.set(saved_default_sort)

# === INITIALIZE SYSTEM-WIDE THEMES AND STATUS BAR LOOP ===
update_system_wide_themes()
update_status_bar()

# === START PROGRAM ===
root.mainloop()