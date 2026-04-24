# Market Basket Analysis & Smart Retail Recommendation System

A capstone project applying market basket analysis to a real-world UK online retail dataset. Association rules mined from 18,668 customer transactions power an interactive Streamlit dashboard that returns product recommendations for any selected item.

---

## What It Does

Given any product, the app returns:
- **Frequently Bought Together** — top 3 products most often purchased in the same basket
- **Cross-Sell Opportunities** — top 3 products that the same customers also tend to buy

---

## Project Structure

```
├── app.py                          # Streamlit web app
├── notebooks/
│   ├── eda.ipynb                   # Full analysis notebook (Apriori, EDA, rule mining)
│   └── rules.csv                   # Generated association rules (used by the app)
├── submission.md                   # Project write-up
├── report.md                       # Technical report
├── rela_btw_support_confodence.png # Support vs confidence scatter plot
├── Capstone Project.pdf            # Final submission PDF
└── MarketBasketAnalysis_Presentation.pptx
```

---

## Setup

### 1. Clone the repo
```bash
git clone <repo-url>
cd capstone-proj
```

### 2. Install dependencies
```bash
pip install streamlit pandas mlxtend
```

### 3. Run the app
```bash
streamlit run app.py
```

---

## Dataset

The analysis uses the **Online Retail dataset** from the UCI Machine Learning Repository:

> [https://archive.ics.uci.edu/dataset/352/online+retail](https://archive.ics.uci.edu/dataset/352/online+retail)

Download `Online Retail.xlsx`, convert to CSV, and place it at `notebooks/OnlineRetail.csv` to re-run the notebook.

---

## Methodology

- **Algorithm**: Apriori (initial analysis) / FP-Growth (final rule generation)
- **Minimum support**: 1.5% — a product pair must appear in at least 1.5% of all UK transactions
- **Minimum confidence**: 20%
- **Rules generated**: 2,795 across 241 products

---

*By Chikamso Ezeaku*
