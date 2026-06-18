# Real Estate Scraper: Immo-Eliza-scraping

## Team

Developed by **Team Polars Bears** as part of the Immo Eliza project.

Team members:

| Name |
|------|
| Iness |     as the Lead manager
| Uzair |     as the Git commander
| Guillermo | as the Data architect
| Hiba |      as the Documentation specialist

We were initially the Pandas, but after switching from the Pandas library to Polars, we became the Polars Bears.

## Description

This project is part of the **Immo Eliza** real estate data pipeline.

The goal is to build a complete scraping pipeline to collect and enrich real estate data in Belgium in order to create a dataset for future machine learning models predicting property prices.

The pipeline collects information from **Immovlan**, gathers data from more than 10,000 properties across Belgium, computes additional geographical features, and exports the final dataset in CSV format.

Main components:

* Property listing extraction
* Property detail scraping
* Asynchronous scraping
* Geographical feature engineering
* Dataset processing and export

---

## Project Structure

```
.
├── data/
│   ├── property_listings.csv
│   └── scraped_properties.csv
│
├── dev/
│   └── exploratory notebooks
│
├── src/
│   ├── async_utils.py
│   ├── geo_utils.py
│   ├── property_details_scraper.py
│   └── property_listings_scraper.py
│
└── main.py
```

---

# Pipeline Overview

The pipeline is executed through `main.py`:

```
Scrape property listings
          |
          v
Extract property URLs
          |
          v
Scrape property details asynchronously
          |
          v
Add geographical features
          |
          v
Merge datasets using property_id
          |
          v
Export final dataset
```

---

# Modules

## main.py

Entry point of the project.

It:

* collects property listings;
* launches the detail scraping pipeline;
* merges listing and property information;
* exports the final dataset.

Run:

```bash
python main.py
```

---

## property_listings_scraper.py

Responsible for collecting property URLs and basic information from Immovlan.

Extracted information includes:

* property ID
* URL
* location
* postal code
* property type
* contract type

---

## property_details_scraper.py

Scrapes detailed information from individual property pages.

Collected data includes:

* price
* property characteristics
* energy information
* facilities
* accessibility distances
* coordinates

---

## geo_utils.py

Adds geographical features:

* driving distance to Brussels using OSRM
* distance to nearest Belgian city using geographical coordinates

---

## async_utils.py

Handles concurrent scraping of multiple property pages.

It improves performance by scraping several pages simultaneously while limiting the number of active requests.

---

# Data Output

The pipeline generates:

### property_listings.csv

Contains basic information about each property:

* URL
* property ID
* location
* property type

### scraped_properties.csv

Final enriched dataset containing:

* listing information
* property features
* geographical features
* accessibility information

---

# Development

The `dev/` folder contains exploratory notebooks used for:

* testing scraping functions
* data exploration
* feature validation

---

# Main libraries

* requests
* beautifulsoup4
* pandas
* polars
* asyncio

---

# Running the project

## How to run the project

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python main.py
```

The final dataset is generated at:

```
data/scraped_properties.csv
```

