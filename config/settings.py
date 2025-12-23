# -*- coding: utf-8 -*-
"""Application settings and configuration"""
import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# App settings
APP_NAME = "ROI RPA Calculator"
APP_VERSION = "1.0.1"
APP_DESCRIPTION = "Professional tool for analyzing ROI of RPA automations"


# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/calculator.db")

# Page Config
PAGE_LAYOUT = "wide"
INITIAL_SIDEBAR_STATE = "collapsed"
