# Market Basket Analysis and Product Recommendation System for Online Retail

**Chikamso Ezeaku**
**ITEC Capstone**
**Frostburg State University**
**April 24, 2026**

---

## Abstract

This project presents a market basket analysis and product recommendation system built on a real-world UK online retail dataset. Using the Apriori algorithm for frequent itemset mining and association rule learning, the study identifies statistically significant product pairings within customer transactions. A total of 155 association rules were generated, of which 63 met strong confidence and lift thresholds. Key findings include dominant collection-driven purchasing behavior within product families, as well as meaningful cross-category purchasing patterns suitable for cross-sell strategy. The analytical findings were operationalized into an interactive web-based dashboard developed in Python using Streamlit, enabling business users to query any product and receive ranked recommendations alongside cross-sell suggestions. The dashboard's user interface was collaboratively designed with Claude (Anthropic), an AI assistant, which contributed the visual layout architecture, CSS styling system, and the cross-sell detection logic. This project demonstrates how classical association rule mining can be integrated into a practical, user-facing retail intelligence tool.

**Keywords:** market basket analysis, association rules, Apriori algorithm, product recommendation, cross-sell, retail analytics, Streamlit

---

## 1. Introduction

Understanding what customers buy together is one of the oldest and most actionable problems in retail analytics. Originally formalized through the "market basket" metaphor — imagining the contents of a single shopping basket — the field of association rule mining has evolved into a core technique for product placement, bundling strategy, and personalized recommendation systems (Agrawal & Srikant, 1994).

This project applies market basket analysis to a publicly available UK online retail dataset to answer two core questions:

1. Which products are most frequently purchased together, and how strong are those associations?
2. Are there cross-category purchasing patterns that represent untapped cross-sell opportunities?

Beyond the analytical exercise, this project goes a step further by translating findings into a live, interactive recommendation dashboard — bridging the gap between data science output and practical business usability. The development of the dashboard involved collaboration with Claude, an AI assistant developed by Anthropic, which contributed to the interface design and algorithmic components described in Section 4.

---

## 2. Dataset

### 2.1 Source

The dataset used in this project is the Online Retail Dataset, a publicly available transactional dataset containing purchases made by customers of a UK-based online gift retailer between December 2010 and December 2011. Each row in the dataset represents a line item within a customer invoice, meaning a single purchase transaction (invoice) may span multiple rows.

### 2.2 Structure

The raw dataset contained 541,909 rows and 8 columns:

| Column      | Description                              |
|-------------|------------------------------------------|
| InvoiceNo   | Unique transaction identifier            |
| StockCode   | Product code                             |
| Description | Product name                             |
| Quantity    | Number of units purchased                |
| InvoiceDate | Date and time of transaction             |
| UnitPrice   | Price per unit (GBP)                     |
| CustomerID  | Customer identifier (nullable)           |
| Country     | Country of the customer                  |

### 2.3 Geographic Distribution

An initial country-level analysis revealed that the dataset is heavily concentrated in the United Kingdom, which accounts for approximately 91.5% of all transactions. The next largest markets — Germany (1.7%), France (1.6%), and EIRE (1.5%) — represent far smaller proportions. Given this imbalance, the analysis was scoped to UK transactions only to ensure the resulting rules reflect coherent purchasing behavior within a single market context.

---

## 3. Methodology

### 3.1 Data Cleaning

Prior to any modeling, a cleaning pipeline was applied to address quality issues identified during initial exploration.

**Missing descriptions.** 1,454 rows contained null values in the Description column. Since product descriptions are the fundamental unit of a basket in this analysis, these rows were removed entirely.

**Whitespace normalization.** Product descriptions contained inconsistent spacing (e.g., leading, trailing, and internal extra spaces). A regular expression substitution was applied to standardize all descriptions to single-space-separated strings. Without this step, identical products with minor formatting differences would be treated as distinct items, inflating the product vocabulary and fragmenting association signals.

**Cancelled transactions.** Invoices prefixed with the letter "C" represent cancellations and returns. Including these would introduce negative purchasing signals that misrepresent actual customer behavior. All such records were excluded.

After cleaning, the dataset contained 531,167 rows. The cleaning approach was deliberately conservative — only records that could not meaningfully contribute to basket analysis were removed.

### 3.2 Transaction Matrix Construction

The analysis was restricted to UK transactions, yielding 18,668 unique invoices. These were reshaped into a transaction matrix: a binary matrix of dimensions 18,668 × 4,134, where rows represent individual invoices and columns represent unique product descriptions. A value of 1 indicates that the product was present in that transaction; 0 indicates it was absent.

Several non-product columns — POSTAGE, DOTCOM, CARRIAGE, and MANUAL — were removed from the matrix, as these represent operational entries rather than purchasable products.

The original quantity values were binarized (presence/absence) rather than retained as counts. For association rule mining, the relevant signal is whether a product appeared in a transaction at all, not how many units were ordered.

### 3.3 Frequent Itemset Mining

The Apriori algorithm (Agrawal & Srikant, 1994) was applied to the binary transaction matrix using the `mlxtend` Python library (Raschka, 2018). A minimum support threshold of 2% (0.02) was selected, meaning only itemsets appearing in at least 2% of all UK transactions were retained. This produced 368 frequent itemsets.

Support thresholds below 1% were considered during experimentation but rejected as they generated an unmanageable number of low-signal itemsets. The 2% threshold was judged to balance coverage with interpretability.

### 3.4 Association Rule Generation

Association rules were derived from the frequent itemsets using the confidence metric with a minimum threshold of 0.3 (30%). This produced 155 rules across 14 metrics, including support, confidence, lift, leverage, and conviction.

Each rule takes the form: *antecedent → consequent*, where the antecedent represents the product(s) already in the basket and the consequent represents the predicted addition.

### 3.5 Rule Filtering

Raw rules were filtered into two analytical tiers:

**Strong paired rules** (for the "Frequently Bought Together" use case):
- Confidence ≥ 0.50
- Lift ≥ 2.0

This yielded 63 rules capturing high-reliability, non-trivial associations.

**Cross-sell rules** (for the "Cross-Sell Opportunities" use case):
- Confidence ≥ 0.30
- Lift ≥ 1.5

Cross-sell rules were additionally filtered using a word-overlap heuristic: if the antecedent and consequent product names share no significant words (words of more than four characters, excluding common descriptors such as "large," "small," "design," and "pattern"), the pair is classified as a cross-category cross-sell. This distinguishes within-family pairings (e.g., two teacup variants) from genuinely distinct product category pairings.

---

## 4. Dashboard Development

### 4.1 Technology Stack

The recommendation system was deployed as an interactive web application using Streamlit, a Python framework for building data applications. The application reads the exported association rules (rules.csv) and enables business users to query recommendations by product without requiring any technical knowledge.

### 4.2 Application Logic

When a product is selected, the application filters the rules dataset for all rules where the selected product appears in the antecedent. These candidates are then split into two groups:

- **Frequently Bought Together:** Rules meeting the strong threshold (confidence ≥ 0.50, lift ≥ 2.0), ranked by support then lift. The top 3 are displayed.
- **Cross-Sell Opportunities:** Rules meeting the relaxed threshold (confidence ≥ 0.30, lift ≥ 1.5) where the consequent product is from a different category, ranked by lift. The top 3 are displayed.

Each recommendation card displays the product name, a business-tier badge (Bundle Opportunity, Strong Recommendation, Recommendation, or Cross-Sell), and three metric pills showing support, confidence, and lift.

### 4.3 AI Collaboration — Claude (Anthropic)

The visual design and interface architecture of the dashboard were developed in collaboration with Claude, an AI assistant by Anthropic. Specific contributions by Claude include:

- **Full UI redesign:** Replacing the default Streamlit layout with a custom CSS styling system featuring a gradient hero banner, dark sidebar, and card-based recommendation layout.
- **Two-section recommendation architecture:** Structuring the application to present "Frequently Bought Together" and "Cross-Sell Opportunities" as distinct, visually differentiated sections.
- **Cross-sell detection logic:** Authoring the `is_cross_sell()` function, which uses a word-overlap heuristic to distinguish same-ecosystem pairings from genuinely cross-category recommendations.
- **Metric visualization:** Designing the metric pill components (support, confidence, lift) displayed within each recommendation card.
- **Product selector placement:** Resolving a usability issue in which the product selector was hidden inside a collapsible sidebar and relocating it to the persistent main page area.

The core analytical pipeline — data cleaning, matrix construction, Apriori execution, rule generation, and filtering — was authored by the student.

---

## 5. Results

### 5.1 Overall Rule Summary

| Stage                        | Count   |
|-----------------------------|---------|
| Raw transactions             | 541,909 |
| After cleaning               | 531,167 |
| UK transactions (invoices)   | 18,668  |
| Products in matrix           | 4,134   |
| Frequent itemsets (≥2%)      | 368     |
| Association rules (≥30% conf)| 155     |
| Strong rules (≥50% conf, ≥2× lift) | 63 |

### 5.2 Top Findings

**Collection behavior (within-family).**
The strongest associations in the dataset involve the Regency Teacup and Saucer collection. Customers who purchase any one variant — Pink, Green, or Roses — are highly likely to purchase the others. The top rule, Pink Regency Teacup → {Green Regency Teacup, Roses Regency Teacup}, achieved a lift of 18.68, meaning that pairing is over 18 times more likely than if the items were purchased independently. This reflects deliberate collection-completion behavior rather than incidental co-purchase.

**Complementary product pairs.**
Outside of collection behavior, strong associations exist between functionally complementary items:

- *Spaceboy Lunch Box ↔ Dolly Girl Lunch Box* — Lift: 16.23. Likely purchased together as a matched pair, possibly as a gift set.
- *Gardeners Kneeling Pad (Cup of Tea) ↔ Gardeners Kneeling Pad (Keep Calm)* — Lift: 14.99. Variant-matching behavior within a themed product line.
- *Charlotte Bag variants* (Woodland, Strawberry, Pink Polkadot, Suki Design) — Lift range: 14.04–15.19. Customers build coordinated bag sets across color and pattern variants.

**Cross-sell patterns.**
At relaxed thresholds, meaningful cross-category associations were identified:

- *Jumbo Bag variants → Jumbo Bag Red Retrospot* — Lift range: 5.59–6.52. The Red Retrospot design functions as an anchor product that customers add alongside other bag purchases, suggesting it holds broader appeal across the bag-buying segment.
- *Alarm Clock Bakelike Red ↔ Alarm Clock Bakelike Green* — Lift: 12.90. Despite appearing as a within-family pair, these represent a genuine cross-sell opportunity where customers collecting the clock range branch across color variants.
- *Roses Regency Teacup → Regency Cakestand 3 Tier* — Lift: 5.25. A table-setting expansion pattern: customers building a coordinated tea service add the cakestand as a functional complement to their cup and saucer purchase.

### 5.3 Business Implications

The findings support three distinct retail strategies:

1. **Bundle packaging.** High-lift collection pairs (Regency Teacups, Charlotte Bags) are strong candidates for pre-packaged bundle offers, reducing the friction of customers manually building sets.
2. **Cross-sell prompts.** Products like Jumbo Bag Red Retrospot and the Regency Cakestand appear in cross-category rules and are well-positioned as "customers also bought" prompts at point of purchase or in post-checkout emails.
3. **Merchandising adjacency.** High-confidence pairs should be physically or digitally co-located — product pages, shelf placement, or category landing pages — to leverage the natural co-purchase tendency identified in the data.

---

## 6. Discussion

### 6.1 Strengths

The project successfully moves from raw transactional data to a deployed, interactive recommendation tool. The two-tier recommendation architecture (paired vs. cross-sell) is a meaningful design decision: it separates the use case of bundle promotion from the use case of category expansion, which serve different business objectives.

The cross-sell detection heuristic, while simple, performs reasonably well on this dataset. Product names in the Online Retail dataset tend to be descriptive and keyword-rich, making word overlap a pragmatic proxy for product family membership.

### 6.2 Limitations

**Support threshold sensitivity.** The 2% minimum support threshold, while practical, excludes many valid low-frequency associations. In a long-tail product catalog, meaningful niche pairings may exist below this threshold.

**UK-only scope.** Restricting to UK transactions was analytically justified but limits generalizability. Purchasing behavior in other markets may reveal different associations.

**No temporal analysis.** The dataset spans a full year, but no seasonal or temporal segmentation was applied. Associations may vary significantly between, for example, the holiday season and off-peak months.

**Word-overlap heuristic.** The cross-sell detection function uses a surface-level word match. Products with unrelated names that happen to share common words (e.g., "RED" in both "ALARM CLOCK BAKELIKE RED" and "JUMBO BAG RED RETROSPOT") may be incorrectly classified as within-family.

### 6.3 Future Work

Future iterations could incorporate collaborative filtering or neural embedding approaches (e.g., Word2Vec applied to product sequences) to capture deeper semantic product relationships. Temporal segmentation would allow seasonal recommendation strategies. Extending the analysis beyond UK transactions could reveal international market differences and enable market-specific recommendation tuning.

---

## 7. Conclusion

This project demonstrates that market basket analysis remains a practical and interpretable technique for extracting purchasing behavior insights from transactional retail data. Using the Apriori algorithm on 18,668 UK transactions, 63 strong association rules were identified, revealing both collection-completion behavior and genuine cross-category purchasing patterns. These findings were operationalized into a Streamlit dashboard that enables non-technical business users to query recommendations interactively. Collaborative development with Claude (Anthropic) contributed the dashboard's visual architecture and cross-sell detection logic, illustrating how AI-assisted development can accelerate the delivery of data products. The resulting system bridges exploratory data analysis and practical business application, offering a template for retail recommendation systems grounded in real customer behavior.

---

## References

Agrawal, R., & Srikant, R. (1994). Fast algorithms for mining association rules. *Proceedings of the 20th International Conference on Very Large Data Bases (VLDB)*, 487–499.

Anthropic. (2024). *Claude* (claude-sonnet-4-6) [Large language model]. https://www.anthropic.com

Chen, D., Sain, S. L., & Guo, K. (2012). Data mining for the online retail industry: A case study of RFM model-based customer segmentation using data mining. *Journal of Database Marketing & Customer Strategy Management, 19*(3), 197–208. https://doi.org/10.1057/dbm.2012.17

Daqing, C. (2015). *Online Retail* [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5BW33

Han, J., Pei, J., & Kamber, M. (2011). *Data mining: Concepts and techniques* (3rd ed.). Morgan Kaufmann.

Raschka, S. (2018). MLxtend: Providing machine learning and data science utilities and extensions to Python's scientific computing stack. *Journal of Open Source Software, 3*(24), 638. https://doi.org/10.21105/joss.00638

---
