# Flexeer Wallet & Auto-Forwarder

## Overview
This project consists of two main components:
1. **Flexeer Wallet**: A Flask-based web application for managing a virtual currency (GIZ).
2. **Auto-Forwarder**: A Telegram bot that forwards Binance crypto box codes from source channels to a target channel.

## Features
- **Wallet**:
    - User registration and login.
    - Signup bonus (5.0 GIZ).
    - Referral system with rewards.
    - Daily rewards.
    - Peer-to-peer transfers.
    - Transaction history.
- **Auto-Forwarder**:
    - Monitors multiple Telegram channels for crypto codes.
    - Automatically forwards valid, unique codes to a target channel.
    - Sends welcome messages and periodic reminders.

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Initialize the database:
   ```bash
   python Flexeer/init_db.py
   ```
3. Run the project:
   ```bash
   bash start.sh
   ```
