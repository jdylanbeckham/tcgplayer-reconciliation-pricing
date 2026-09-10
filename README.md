# Trading Card Acquisition, Pricing & Inventory Optimization — Publishable Dataset

## Purpose
This package is the publishable data foundation for the PPAD flagship reconstruction. It preserves real historical card, set, pricing, quantity, and merchant context while organizing the evidence for reproducible Python/pandas work.

## Contents

### raw_examples/
- `tcgplayer_mypricing_export.csv` — historical TCGplayer export supplied as an example of the external marketplace format.
- `trader_tools_export.csv` — historical Trader Tools export supplied as an example of the market-pricing feed. The source ODS had no header row; column names were applied from the matching `TT Data` schema in the historical TOM Pricing Database. Vendor names are intentionally retained because they materially explain the pricing-source context.

### reconstruction_inputs/
- `tcgplayer_inventory_input.csv` — the `Inventory Data To Match Against` sheet extracted from the historical TOM Pricing Database.
- `trader_tools_market_input.csv` — the `TT Data` sheet extracted from the same historical workbook.

These two files are the preferred paired inputs for reconstructing the historical workflow because they originate from the same workbook state.

### reference_outputs/
- `historical_processing_reference.csv` — historical intermediate processing output.
- `historical_export_reference.csv` — historical export/output reference.
- `historical_buylist_reference.csv` — historical buylist/reference output.

These files are validation references for the reconstruction. They are not assumed to represent a modernized implementation.

## Publication disposition
Original historical data is intentionally retained where it improves understanding. No default anonymization was applied. Merchant/vendor names are preserved. Publication remains subject to the approved PPAD Public Artifact Publication Standard.

A basic scan of the relevant historical workbook sheets found no email addresses, phone numbers, URLs, or obvious credential/secret strings.

## Important comparison note
The standalone raw-example exports are examples of external source formats and should not be assumed to be the exact temporal pair used by the historical TOM workbook. For row-level reconstruction and validation, use the files in `reconstruction_inputs/` with the files in `reference_outputs/`.

## Intended next use
ACT-115 will use the paired reconstruction inputs to rebuild the reconciliation workflow in Python/pandas, with explicit matching, validation, exception reporting, and reproducible outputs.
