#!/usr/bin/env python3
"""
Database Setup Script for Task Tracker Application

This script initializes the SQLite database with required tables and 
optionally populates it with sample data.
"""

import argparse
import os
from init_db import init_database, populate_sample_data


def main():
    parser = argparse.ArgumentParser(description='Setup Task Tracker Database')
    parser.add_argument('--sample-data', action='store_true', 
                        help='Populate database with sample data')
    
    args = parser.parse_args()
    
    print("Initializing database...")
    init_database()
    
    if args.sample_data:
        print("Adding sample data...")
        populate_sample_data()
    
    print("Database setup complete!")


if __name__ == "__main__":
    main()