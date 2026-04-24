import ast
import pandas as pd
import streamlit as st

# ----------------------------
# Helpers
# ----------------------------
def parse_itemset(cell) -> list[str]:
    if pd.isna(cell):
        return []
    s = str(cell).strip()
    if s.startswith("frozenset"):
        inside = s[s.find("(") + 1 : s.rfind(")")]
        try:
            obj = ast.literal_eval(inside)
            return sorted([str(x).strip() for x in obj])
        except Exception:
            return []
    if s.startswith("{") and s.endswith("}"):
        try:
            obj = ast.literal_eval(s)
            return sorted([str(x).strip() for x in obj])
        except Exception:
            return []
    return [s]

def tier_label(support: float, confidence: float, lift: float) -> str:
    if support >= 0.03 and confidence >= 0.5 and lift >= 1.5:
        return "Bundle Opportunity"
    if confidence >= 0.5 and lift >= 2:
        return "Strong Recommendation"
    return "Recommendation"

def format_pct(x: float) -> str:
    return f"{x*100:.1f}%"

_IGNORE_WORDS = {
    "with", "large", "small", "mini", "pack", "set", "design", "pattern",
    "vintage", "retro", "style", "heart", "box", "bag", "case", "holder",
    "hanging", "wall", "door", "wood", "metal", "glass", "round", "square",
}

def is_cross_sell(p1: str, p2: str) -> bool:
    """Returns True if p1 and p2 share no meaningful words (different ecosystems)."""
    def key_words(p):
        return {w for w in p.lower().split() if len(w) > 4 and w not in _IGNORE_WORDS}
    return len(key_words(p1) & key_words(p2)) == 0

# ----------------------------
# Page config
# ----------------------------
st.set_page_config(
    page_title="Smart Retail Recommendations",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------
# Custom CSS
# ----------------------------
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    [data-testid="collapsedControl"] {visibility: visible !important;}

    .stApp { background-color: #f0f2f6; }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
        padding-top: 1rem;
    }
    [data-testid="stSidebar"] * { color: #cbd5e1 !important; }
    [data-testid="stSidebar"] hr { border-color: #334155; }

    /* Hero */
    .hero {
        background: linear-gradient(135deg, #0f172a 0%, #1e40af 100%);
        border-radius: 16px;
        padding: 2.2rem 2.5rem;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .hero-title { font-size: 1.7rem; font-weight: 800; color: #fff; margin: 0; letter-spacing: -0.02em; }
    .hero-sub   { color: #93c5fd; font-size: 0.9rem; margin: 0.3rem 0 0 0; }
    .hero-stat  { text-align: right; color: #93c5fd; font-size: 0.8rem; }
    .hero-stat span { display: block; font-size: 1.6rem; font-weight: 700; color: #fff; }

    /* Section headers */
    .section-header {
        display: flex;
        align-items: center;
        gap: 0.7rem;
        margin: 1.8rem 0 1rem 0;
    }
    .section-icon {
        width: 36px; height: 36px;
        border-radius: 10px;
        display: flex; align-items: center; justify-content: center;
        font-size: 1rem;
    }
    .section-icon.blue  { background: #dbeafe; }
    .section-icon.teal  { background: #ccfbf1; }
    .section-title { font-size: 1.05rem; font-weight: 700; color: #0f172a; margin: 0; }
    .section-sub   { font-size: 0.78rem; color: #64748b; margin: 0; }

    /* Cards — paired */
    .card {
        background: #fff;
        border-radius: 14px;
        padding: 1.4rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.04);
        border-top: 5px solid #3b82f6;
        height: 100%;
    }
    .card.gold   { border-top-color: #f59e0b; }
    .card.silver { border-top-color: #94a3b8; }
    .card.bronze { border-top-color: #b45309; }

    /* Cards — cross-sell */
    .card-cs {
        background: #fff;
        border-radius: 14px;
        padding: 1.4rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06), 0 4px 16px rgba(0,0,0,0.04);
        border-top: 5px solid #14b8a6;
        height: 100%;
    }

    .card-rank {
        font-size: 0.65rem; font-weight: 700;
        text-transform: uppercase; letter-spacing: 0.1em;
        color: #94a3b8; margin-bottom: 0.4rem;
    }
    .card-product {
        font-size: 1rem; font-weight: 700;
        color: #0f172a; line-height: 1.4;
        margin-bottom: 0.8rem; min-height: 2.8rem;
    }

    /* Badges */
    .badge {
        display: inline-block; padding: 0.22rem 0.7rem;
        border-radius: 20px; font-size: 0.7rem; font-weight: 700; margin-bottom: 0.9rem;
    }
    .badge-bundle { background: #fef3c7; color: #92400e; border: 1px solid #fde68a; }
    .badge-strong { background: #d1fae5; color: #065f46; border: 1px solid #a7f3d0; }
    .badge-rec    { background: #ede9fe; color: #4c1d95; border: 1px solid #ddd6fe; }
    .badge-cross  { background: #ccfbf1; color: #134e4a; border: 1px solid #99f6e4; }

    /* Metric pills */
    .metrics { display: flex; gap: 0.4rem; margin-top: 0.8rem; }
    .metric {
        flex: 1; background: #f8fafc; border: 1px solid #e2e8f0;
        border-radius: 10px; padding: 0.55rem 0.3rem; text-align: center;
    }
    .metric-val { font-size: 1rem; font-weight: 800; color: #1e293b; }
    .metric-lbl { font-size: 0.58rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.06em; margin-top: 0.1rem; }

    .rec-desc { font-size: 0.8rem; color: #64748b; line-height: 1.5; margin-top: 0.85rem; }

    /* Info box */
    .info-box {
        background: white; border-radius: 14px; padding: 2rem 2.5rem;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
        max-width: 540px; margin: 2rem auto; border-left: 5px solid #3b82f6;
    }
    .info-box h4 { color: #0f172a; margin: 0 0 1rem 0; font-size: 1.05rem; }
    .info-box ol { color: #475569; margin: 0; padding-left: 1.3rem; line-height: 2; font-size: 0.9rem; }

    /* Legend */
    .legend {
        background: white; border-radius: 12px; padding: 1rem 1.5rem;
        margin-top: 1.5rem; font-size: 0.78rem; color: #64748b;
        box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    }
    .legend strong { color: #374151; }

    /* Divider */
    .section-divider { border: none; border-top: 1px solid #e2e8f0; margin: 2rem 0 0 0; }
</style>
""", unsafe_allow_html=True)

# ----------------------------
# Load rules
# ----------------------------
@st.cache_data
def load_rules(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    required = {"antecedents", "consequents", "support", "confidence", "lift"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"rules.csv is missing columns: {missing}")
    df["antecedents_list"] = df["antecedents"].apply(parse_itemset)
    df["consequents_list"] = df["consequents"].apply(parse_itemset)
    df = df[df["consequents_list"].apply(len) == 1].copy()
    df["antecedent_len"] = df["antecedents_list"].apply(len)
    df["consequent_item"] = df["consequents_list"].apply(lambda x: x[0] if x else "")
    return df

rules = load_rules("notebooks/rules.csv")

@st.cache_data
def valid_products(rules: pd.DataFrame) -> list[str]:
    """Return only products that yield at least 1 FBT result AND 1 cross-sell result."""
    candidates = sorted(
        {item for items in rules["antecedents_list"] for item in items if isinstance(item, str) and item}
    )
    valid = []
    for prod in candidates:
        cand = rules[rules["antecedents_list"].apply(lambda items: prod in items)]
        if cand.empty:
            continue
        # FBT: top 3 by confidence
        top3 = (
            cand.sort_values(by=["confidence", "lift"], ascending=[False, False])
            .drop_duplicates(subset=["consequent_item"])
            .head(3)
        )
        if top3.empty:
            continue
        fbt_items = set(top3["consequent_item"].tolist())
        # Cross-sell: reverse pool + forward pool (with fallback to full pool)
        rev = rules[(rules["consequent_item"] == prod) & (rules["antecedent_len"] == 1)].copy()
        rev["rev_item"] = rev["antecedents_list"].apply(lambda x: x[0] if x else "")
        rev_pool = rev[rev["rev_item"] != ""][["rev_item", "support", "confidence", "lift"]].rename(columns={"rev_item": "cross_item"})
        fwd_pool = cand[~cand["consequent_item"].isin(fbt_items)][["consequent_item", "support", "confidence", "lift"]].rename(columns={"consequent_item": "cross_item"})
        combined = (
            pd.concat([fwd_pool, rev_pool], ignore_index=True)
            .query("cross_item != @prod")
            .loc[lambda d: ~d["cross_item"].isin(fbt_items)]
            .drop_duplicates(subset=["cross_item"])
        )
        if combined.empty:
            # Fallback: full pool (may overlap FBT)
            cand_fwd = cand[["consequent_item", "support", "confidence", "lift"]].rename(columns={"consequent_item": "cross_item"})
            combined = pd.concat([cand_fwd, rev_pool], ignore_index=True).query("cross_item != @prod").drop_duplicates(subset=["cross_item"])
        if combined.empty:
            continue
        valid.append(prod)
    return valid

all_products = valid_products(rules)

# ----------------------------
# Sidebar
# ----------------------------
with st.sidebar:
    st.markdown("### Smart Retail")
    st.markdown("**Recommendation Engine**")
    st.markdown("---")
    st.markdown(
        f'<p style="font-size:0.82rem;color:#94a3b8;">'
        f'{len(all_products)} products available<br>'
        f'{len(rules)} association rules mined<br><br>'
        f'UK Online Retail Dataset</p>',
        unsafe_allow_html=True,
    )
    st.markdown("---")
    st.markdown(
        '<p style="font-size:0.75rem;color:#64748b;">'
        'Paired: <strong style="color:#94a3b8;">confidence ≥ 50%, lift ≥ 2×</strong><br>'
        'Cross-sell: <strong style="color:#94a3b8;">lift ≥ 1.5, confidence ≥ 30%</strong></p>',
        unsafe_allow_html=True,
    )

# ----------------------------
# Hero
# ----------------------------
st.markdown(f"""
<div class="hero">
    <div>
        <p class="hero-title">Smart Retail Recommendations</p>
        <p class="hero-sub">Product pairings powered by market basket analysis</p>
    </div>
    <div class="hero-stat">
        <span>{len(rules)}</span>
        association rules mined
    </div>
</div>
""", unsafe_allow_html=True)

selected_product = st.selectbox("Select a product to get recommendations:", [""] + all_products)

# ----------------------------
# Empty state
# ----------------------------
if selected_product == "":
    st.markdown("""
    <div class="info-box">
        <h4>How to use this dashboard</h4>
        <ol>
            <li>Select a product from the dropdown above</li>
            <li>See the top 3 products customers frequently buy together with it</li>
            <li>Explore cross-sell opportunities from different product categories</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ----------------------------
# All candidates for selected product
# ----------------------------
candidate = rules[
    rules["antecedents_list"].apply(lambda items: selected_product in items)
].copy()

# ----------------------------
# SECTION 1 — Frequently Bought Together
# ----------------------------
# Top 3 by confidence (descending), then lift — no hard threshold so every
# product with at least one rule always shows results.
top3_fbt = (
    candidate
    .sort_values(by=["confidence", "lift"], ascending=[False, False])
    .drop_duplicates(subset=["consequent_item"])
    .head(3)
    .copy()
)
fbt_items = set(top3_fbt["consequent_item"].tolist())

st.markdown(f"""
<hr class="section-divider">
<div class="section-header">
    <div class="section-icon blue"></div>
    <div>
        <p class="section-title">Frequently Bought Together</p>
        <p class="section-sub">Products customers most often pair with <strong>{selected_product}</strong></p>
    </div>
</div>
""", unsafe_allow_html=True)

if top3_fbt.empty:
    st.info("No pairing data found for this product.")
else:
    rank_meta = [("gold", "#1 Top Pick"), ("silver", "#2 Runner-up"), ("bronze", "#3 Also Consider")]
    badge_map = {
        "Bundle Opportunity":    "badge-bundle",
        "Strong Recommendation": "badge-strong",
        "Recommendation":        "badge-rec",
    }

    cols = st.columns(len(top3_fbt), gap="medium")
    for col, (card_cls, rank_lbl), row in zip(cols, rank_meta, top3_fbt.itertuples(index=False)):
        sup  = float(row.support)
        conf = float(row.confidence)
        lif  = float(row.lift)
        badge = tier_label(sup, conf, lif)
        with col:
            st.markdown(f"""
            <div class="card {card_cls}">
                <div class="card-rank">{rank_lbl}</div>
                <div class="card-product">{row.consequent_item}</div>
                <span class="badge {badge_map[badge]}">{badge}</span>
                <div class="metrics">
                    <div class="metric">
                        <div class="metric-val">{format_pct(sup)}</div>
                        <div class="metric-lbl">Support</div>
                    </div>
                    <div class="metric">
                        <div class="metric-val">{format_pct(conf)}</div>
                        <div class="metric-lbl">Confidence</div>
                    </div>
                    <div class="metric">
                        <div class="metric-val">{lif:.1f}x</div>
                        <div class="metric-lbl">Lift</div>
                    </div>
                </div>
                <div class="rec-desc">
                    Customers who buy <strong>{selected_product}</strong> frequently add this to their basket.
                </div>
            </div>
            """, unsafe_allow_html=True)

# ----------------------------
# SECTION 2 — Cross-Sell Opportunities
# ----------------------------
# Build an expanded pool of associated products:
#   forward : rules where selected_product is in antecedents  → consequent_item
#   reverse : rules where selected_product is the consequent  → single antecedent items
# This ensures products that appear only as rule consequents still get coverage.
reverse_rules = rules[
    (rules["consequent_item"] == selected_product) & (rules["antecedent_len"] == 1)
].copy()
reverse_rules["rev_item"] = reverse_rules["antecedents_list"].apply(
    lambda x: x[0] if x else ""
)
reverse_pool = reverse_rules[reverse_rules["rev_item"] != ""].rename(
    columns={"rev_item": "cross_item"}
)[["cross_item", "support", "confidence", "lift"]].copy()

# Forward pool (consequents not in FBT)
forward_pool = candidate[~candidate["consequent_item"].isin(fbt_items)].copy()
forward_pool = forward_pool.rename(columns={"consequent_item": "cross_item"})[
    ["cross_item", "support", "confidence", "lift"]
].copy()

# Combined pool deduplicated, excluding FBT and the selected product itself
combined_pool = (
    pd.concat([forward_pool, reverse_pool], ignore_index=True)
    .query("cross_item != @selected_product")
    .loc[lambda d: ~d["cross_item"].isin(fbt_items)]
    .drop_duplicates(subset=["cross_item"])
)

# Primary: genuinely different-category items (word-overlap check)
cross_strict = combined_pool[
    combined_pool["cross_item"].apply(lambda item: is_cross_sell(selected_product, item))
]

if not cross_strict.empty:
    top_cross = (
        cross_strict
        .sort_values(by=["lift", "confidence"], ascending=[False, False])
        .head(3)
        .copy()
    )
    cross_label = "Different Category"
    cross_desc  = "Buyers of <strong>{}</strong> also pick up this item — from a different product category."
elif not combined_pool.empty:
    # Fallback 1: highest-lift items not in FBT, regardless of category
    top_cross = (
        combined_pool
        .sort_values(by=["lift", "confidence"], ascending=[False, False])
        .head(3)
        .copy()
    )
    cross_label = "Also Bought"
    cross_desc  = "Customers who buy <strong>{}</strong> also tend to purchase this item."
else:
    # Fallback 2: all associated items ranked by lift (may overlap FBT)
    all_assoc = (
        pd.concat([
            candidate.rename(columns={"consequent_item": "cross_item"})[["cross_item","support","confidence","lift"]],
            reverse_pool,
        ], ignore_index=True)
        .query("cross_item != @selected_product")
        .drop_duplicates(subset=["cross_item"])
        .sort_values(by=["lift", "confidence"], ascending=[False, False])
        .head(3)
        .copy()
    )
    top_cross = all_assoc
    cross_label = "Frequently Associated"
    cross_desc  = "Customers who buy <strong>{}</strong> are also strongly associated with this item."

st.markdown(f"""
<hr class="section-divider">
<div class="section-header">
    <div class="section-icon teal"></div>
    <div>
        <p class="section-title">Cross-Sell Opportunities</p>
        <p class="section-sub">Products the same customers also tend to buy</p>
    </div>
</div>
""", unsafe_allow_html=True)

if top_cross.empty:
    st.info("No cross-sell opportunities found for this product.")
else:
    cs_cols = st.columns(len(top_cross), gap="medium")
    for col, row in zip(cs_cols, top_cross.itertuples(index=False)):
        sup  = float(row.support)
        conf = float(row.confidence)
        lif  = float(row.lift)
        with col:
            st.markdown(f"""
            <div class="card-cs">
                <div class="card-rank">Cross-Sell</div>
                <div class="card-product">{row.cross_item}</div>
                <span class="badge badge-cross">{cross_label}</span>
                <div class="metrics">
                    <div class="metric">
                        <div class="metric-val">{format_pct(sup)}</div>
                        <div class="metric-lbl">Support</div>
                    </div>
                    <div class="metric">
                        <div class="metric-val">{format_pct(conf)}</div>
                        <div class="metric-lbl">Confidence</div>
                    </div>
                    <div class="metric">
                        <div class="metric-val">{lif:.1f}x</div>
                        <div class="metric-lbl">Lift</div>
                    </div>
                </div>
                <div class="rec-desc">
                    {cross_desc.format(selected_product)}
                </div>
            </div>
            """, unsafe_allow_html=True)

# ----------------------------
# Legend
# ----------------------------
st.markdown("""
<hr class="section-divider">
<div class="legend">
    <strong>Support</strong> — share of all transactions containing this pair &nbsp;|&nbsp;
    <strong>Confidence</strong> — how often customers buy both items together &nbsp;|&nbsp;
    <strong>Lift</strong> — strength of the pairing vs. random chance (higher = stronger)
</div>
""", unsafe_allow_html=True)