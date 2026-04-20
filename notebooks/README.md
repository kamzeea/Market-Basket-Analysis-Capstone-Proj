Market Basket Analysis & Product Bundling

Week 1: Data Exploration & Cleaning

Objective

The goal of Week 1 was to understand the structure and quality of the dataset and prepare it for transaction-based analysis. This phase focused on inspecting the data, identifying issues, and applying minimal but necessary cleaning steps.

Dataset

Source: Online Retail Dataset

Each row in the dataset represents a product purchased as part of an invoice. A single transaction (invoice) can include multiple products, meaning multiple rows may belong to the same transaction.

Key columns examined:

InvoiceNo – transaction identifier

Description – product name

Quantity – number of units purchased

Country – customer location

Data Inspection

Initial exploration was performed to understand:

Dataset dimensions (rows and columns)

Column names and data types

Missing values

General data consistency

This helped identify issues that could affect later analysis.

Data Cleaning Steps

The following cleaning decisions were made:

Removed rows with missing product descriptions
Transactions without a product description cannot be used for basket analysis.

Cleaned product descriptions
Extra spaces were removed from product names to avoid duplicate groupings caused by formatting inconsistencies.

Removed canceled transactions
Invoices starting with “C” were excluded to ensure only completed purchases were analyzed.

These steps were intentionally kept minimal to preserve as much original data as possible.

Country-Level Overview

To understand the geographic distribution of transactions:

Transaction counts were calculated using unique invoice numbers per country

The analysis showed that the dataset is heavily dominated by transactions from the United Kingdom

This insight informed later decisions but no filtering was applied during Week 1.

Summary of Week 1

By the end of Week 1:

The dataset structure and limitations were clearly understood

Key data quality issues were identified and addressed

Cleaned data was prepared for transaction-level analysis

This groundwork ensures the data is reliable and ready for basket construction and pattern discovery in the next phase.