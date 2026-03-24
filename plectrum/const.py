"""Constants for Plectrum Core SDK."""

import os

# Default cloud API configuration
DEFAULT_CLOUD_HOST = "https://api.isingq.com"
DEFAULT_API_KEY_ENV = "PLECTRUM_API_KEY"

# Local solver default configuration
DEFAULT_LOCAL_HOST = "http://192.168.137.100:5001"
DEFAULT_LOCAL_API_PATH = "/api/v1/job/"

# HTTP headers
DEFAULT_CHANNEL = "sdk"

# Question types (problem types)
# Cloud platform: 1=QUBO, 2=ISING
QUBO_PROBLEM = 1
ISING_PROBLEM = 2

# Local solver type strings
LOCAL_TYPE_QUBO = "binary"
LOCAL_TYPE_ISING = "spin"

# Gear (gear) modes
GEAR_FAST = 0      # 快速模式 (Fast mode)
GEAR_BALANCED = 1  # 均衡模式 (Balanced mode)
GEAR_PRECISE = 2  # 精准模式 (Precise mode)

# Computer types (solver machines)
OEPO_ISING_1601 = 1  # OEPO ISING 1601
