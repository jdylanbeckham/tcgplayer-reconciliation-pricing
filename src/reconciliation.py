"""
TCGplayer Inventory Reconciliation and Pricing Workflow

Reconciles TCGplayer inventory records against Trader Tools market data using
explicit normalized Name + Edition keys, reconstructs validated historical
business rules, and produces auditable reconciliation and exception outputs.
"""

from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent.parent

TCGPLAYER_INPUT = (
    PROJECT_ROOT
    / "data"
    / "reconstruction_inputs"
    / "tcgplayer_inventory_input.csv"
)

TRADER_TOOLS_INPUT = (
    PROJECT_ROOT
    / "data"
    / "reconstruction_inputs"
    / "trader_tools_market_input.csv"
)

RECONCILIATION_OUTPUT = (
    PROJECT_ROOT
    / "outputs"
    / "reconciliation"
    / "modernized_reconciliation_output.csv"
)

EXCEPTION_OUTPUT = (
    PROJECT_ROOT
    / "outputs"
    / "exceptions"
    / "reconciliation_exceptions.csv"
)


def normalize_name(series):
    """Normalize card names for deterministic matching."""
    return (
        series.astype("string")
        .str.strip()
        .str.lower()
        .str.replace("æ", "ae", regex=False)
    )


def normalize_edition(series):
    """Normalize edition names for deterministic matching."""
    return (
        series.astype("string")
        .str.strip()
        .str.lower()
    )
def load_inputs():
    """Load the TCGplayer inventory and Trader Tools market datasets."""
    tcgplayer = pd.read_csv(TCGPLAYER_INPUT)
    trader_tools = pd.read_csv(TRADER_TOOLS_INPUT)

    return tcgplayer, trader_tools


def prepare_match_keys(tcgplayer, trader_tools):
    """Create normalized Name + Edition keys used for reconciliation."""
    tcgplayer = tcgplayer.copy()
    trader_tools = trader_tools.copy()

    tcgplayer["match_name"] = normalize_name(tcgplayer["Name"])
    tcgplayer["match_edition"] = normalize_edition(tcgplayer["Edition"])

    trader_tools["match_name"] = normalize_name(trader_tools["cardName"])
    trader_tools["match_edition"] = normalize_edition(trader_tools["setName"])

    return tcgplayer, trader_tools


def reconcile_records(tcgplayer, trader_tools):
    """Reconcile TCGplayer inventory against Trader Tools market data."""
    tcgplayer, trader_tools = prepare_match_keys(
        tcgplayer,
        trader_tools
    )

    market_data = trader_tools[
        [
            "match_name",
            "match_edition",
            "sellPrice",
        ]
    ].copy()

    market_data["sellPrice"] = pd.to_numeric(
        market_data["sellPrice"],
        errors="coerce"
    )

    reconciliation = tcgplayer.merge(
        market_data,
        on=["match_name", "match_edition"],
        how="left",
        validate="many_to_one",
        indicator=True
    )

    reconciliation["Reconstructed Tradelist Count"] = (
        pd.to_numeric(
            reconciliation["Count"],
            errors="coerce"
        ).clip(upper=8)
    )

    reconciliation["Trader Tools Sell Price"] = (
        reconciliation["sellPrice"]
    )

    reconciliation["Reconstructed My Price"] = (
        reconciliation["sellPrice"]
    )

    reconciliation["Reconciliation Status"] = (
        reconciliation["_merge"]
        .map({
            "both": "Matched",
            "left_only": "Exception"
        })
        .astype("object")
    )

    return reconciliation


def classify_exceptions(reconciliation, trader_tools):
    """Assign a specific reason to each unmatched reconciliation record."""
    reconciliation = reconciliation.copy()

    trader_tools_names = set(
        normalize_name(trader_tools["cardName"]).dropna()
    )

    trader_tools_editions = set(
        normalize_edition(trader_tools["setName"]).dropna()
    )

    reconciliation["Exception Reason"] = None

    unmatched = reconciliation["_merge"].eq("left_only")

    split_card = (
        unmatched
        & reconciliation["Name"].str.contains("//", regex=False, na=False)
    )

    name_found = reconciliation["match_name"].isin(trader_tools_names)
    edition_found = reconciliation["match_edition"].isin(trader_tools_editions)

    reconciliation.loc[
        split_card,
        "Exception Reason"
    ] = "Split card absent from Trader Tools"

    reconciliation.loc[
        unmatched & ~split_card & ~name_found & edition_found,
        "Exception Reason"
    ] = "Card name absent from Trader Tools"

    reconciliation.loc[
        unmatched & ~split_card & name_found & edition_found,
        "Exception Reason"
    ] = "Name and edition exist, but pair does not match"

    reconciliation.loc[
        unmatched & ~split_card & name_found & ~edition_found,
        "Exception Reason"
    ] = "Edition absent from Trader Tools"

    reconciliation.loc[
        unmatched & ~split_card & ~name_found & ~edition_found,
        "Exception Reason"
    ] = "Name and edition absent from Trader Tools"

    return reconciliation


def export_results(reconciliation):
    """Export the complete reconciliation and exception datasets."""
    RECONCILIATION_OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    EXCEPTION_OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    export_columns = [
        "Count",
        "Tradelist Count",
        "Name",
        "Edition",
        "Card Number",
        "Condition",
        "Language",
        "Foil",
        "Signed",
        "Artist Proof",
        "Altered Art",
        "Misprint",
        "Promo",
        "Textless",
        "My Price",
        "Rarity",
        "Price",
        "Reconstructed Tradelist Count",
        "Trader Tools Sell Price",
        "Reconstructed My Price",
        "Reconciliation Status",
        "Exception Reason",
    ]

    reconciliation[
        export_columns
    ].to_csv(
        RECONCILIATION_OUTPUT,
        index=False
    )

    exceptions = reconciliation[
        reconciliation["Reconciliation Status"].eq("Exception")
    ].copy()

    exceptions.to_csv(
        EXCEPTION_OUTPUT,
        index=False
    )

    return exceptions


def main():
    """Run the complete reconciliation workflow."""
    tcgplayer, trader_tools = load_inputs()

    reconciliation = reconcile_records(
        tcgplayer,
        trader_tools
    )

    reconciliation = classify_exceptions(
        reconciliation,
        trader_tools
    )

    exceptions = export_results(reconciliation)

    matched_count = (
        reconciliation["Reconciliation Status"]
        .eq("Matched")
        .sum()
    )

    print("TCGplayer Inventory Reconciliation")
    print("----------------------------------")
    print(f"Source records: {len(tcgplayer)}")
    print(f"Matched records: {matched_count}")
    print(f"Exception records: {len(exceptions)}")
    print()
    print(f"Reconciliation output: {RECONCILIATION_OUTPUT}")
    print(f"Exception output: {EXCEPTION_OUTPUT}")


if __name__ == "__main__":
    main()
