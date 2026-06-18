# Real Estate Scraper: Immo Eliza-scraping

## Team

Developed by **Team Polar(s) Bears** as part of the Immo Eliza project.

Team members:

| Name | Role |
|------|------|
| Iness | Project Lead |
| Uzair | Git Commander |
| Guillermo | Data Architect |
| Hiba | Documentation Specialist |

We were initially the Pandas, but after deciding to switch from the Pandas library to Polars, we became the Polar(s) Bears.

## Description

This project is part of the **Immo Eliza** real estate data pipeline.

The goal is to build a complete scraping pipeline to collect and enrich real estate data in Belgium in order to create a dataset for future machine learning models predicting property prices.

The pipeline collects information from **Immovlan**, gathers data from around 10,000 properties across Belgium, computes additional geographical features, and exports the final dataset in CSV format.

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
│   ├── property_listings_scraper.py
│   └── utils.py
│
├── emissions.py
├── main.py
├── .gitignore
└── requirements.txt

```

---

## Pipeline Overview

The pipeline is executed through `main.py`:

```
Scrape property listings (async, all provinces)
          |
          v
Save listings to property_listings.csv
          |
          v
Reload listings CSV → extract property URLs
          |
          v
Scrape property details for each URL (async)
          |
          v
Join listings + details on property_id
          |
          v
Export final dataset to scraped_properties.csv
```

---

## Modules

### main.py

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

### property_listings_scraper.py

Responsible for collecting property URLs and basic information from Immovlan.

Extracted information includes:

* property ID
* URL
* location
* postal code
* property type
* contract type

---

### property_details_scraper.py

Scrapes detailed information from individual property pages.

Collected data includes:

* price
* property characteristics
* energy information
* facilities
* accessibility distances
* coordinates

---

### geo_utils.py

Adds geographical features:

* driving distance to Brussels using OSRM
* distance to nearest Belgian city using geographical coordinates

---

### async_utils.py

Handles concurrent scraping of multiple property pages.

It improves performance by scraping several pages simultaneously while limiting the number of active requests.

---

## Data Output

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

## Development

The `dev/` folder contains exploratory notebooks used for:

* testing scraping functions
* data exploration
* feature validation

---

## Main libraries

* asyncio
* codecarbon
* beautifulsoup4
* httpx
* lxml
* polars

---

## How to run the project

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Run the application:

```bash
python main.py
```

3. The final dataset is generated at:

```
data/scraped_properties.csv
```