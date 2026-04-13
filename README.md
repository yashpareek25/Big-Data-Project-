# Big Data Pipeline - Medallion Architecture

## Project Overview
This project implements a Medallion Architecture based data pipeline 
using AWS S3 and Azure Cloud Services.

## Tech Stack
- AWS S3 - Raw data storage
- Azure Data Lake Storage Gen2 - Cloud storage
- Azure Databricks - Data processing
- Python - Pipeline scripting
- SQL - Data transformation

## Architecture
Raw JSON Data → AWS S3 (Bronze) → Azure Data Lake → Silver Layer → Gold Layer

## Layers
- Bronze Layer - Raw JSON data ingested from AWS S3
- Silver Layer - Cleaned and transformed data with SCD Type 2 logic
- Gold Layer - Aggregated data ready for analytics

## Project Structure
big_data.py/
├── .env
├── .gitignore
├── s3_uploader.py
├── azure_bigdata.py
└── README.md

## Author
Yash Pareek
2022BTECH115
JK Lakshmipat University