##### \# Trading Card Acquisition, Pricing \& Inventory Optimization System

##### 

##### A reconstructed and modernized inventory reconciliation and pricing workflow

##### built from a historical trading-card retail operation.



This repository demonstrates how a spreadsheet-based operational system used

for high-volume Magic: The Gathering inventory management was reconstructed,

validated, and converted into a reproducible Python/pandas workflow.



\## Project Context



The original workflow supported a trading-card business processing thousands

of inventory records across approximately 4,000+ SKUs.



The operating process combined:



\- TCGplayer inventory data

\- Trader Tools market-pricing data

\- spreadsheet-based reconciliation

\- inventory quantity controls

\- pricing updates

\- exception review



The historical spreadsheet workflow emphasized operational speed and ease of

use. Fresh exports could be copied into the workbook and thousands of records

processed quickly, with a relatively small number of exceptions handled

manually.



This project preserves that practical business logic while replacing fragile

spreadsheet matching with explicit, testable Python transformations.



\## Reconstructed Workflow



The modernized workflow:



1\. Loads TCGplayer inventory records.

2\. Loads Trader Tools market-pricing records.

3\. Normalizes card names and edition names.

4\. Reconciles records using an explicit `Name + Edition` key.

5\. Validates the relationship as many-to-one.

6\. Applies the reconstructed inventory business rule:

&#x20;  `Tradelist Count = MIN(Count, 8)`.

7\. Assigns Trader Tools `sellPrice` to successfully matched records.

8\. Retains unmatched records as explicit exceptions.

9\. Classifies the reason each exception failed to reconcile.

10\. Exports auditable reconciliation and exception datasets.



\## Validation Results



The reconstructed workflow was tested against 4,368 historical TCGplayer

inventory records.



| Validation Measure | Result |

| --- | ---: |

| Source inventory records | 4,368 |

| Successfully reconciled records | 4,257 |

| Explicit exceptions | 111 |

| Source names preserved | 100% |

| Source editions preserved | 100% |

| Source counts preserved | 100% |

| Tradelist Count rule validated | 4,368 / 4,368 |

| Matched pricing rule validated | 4,257 / 4,257 |



The standalone Python implementation independently reproduced the results

established during notebook-based reconstruction and validation.



\## Exception Analysis



The 111 unmatched records are retained rather than silently force-matched.



| Exception Type | Records |

| --- | ---: |

| Card name absent from Trader Tools | 76 |

| Split card absent from Trader Tools | 16 |

| Name and edition exist, but pair does not match | 15 |

| Edition absent from Trader Tools | 2 |

| Name and edition absent from Trader Tools | 2 |



This makes unresolved data-quality and source-coverage conditions visible and

auditable.



\## Historical Findings



\### Ae / Æ Naming Difference



Trader Tools and TCGplayer represented some card names differently, such as

`Aetherling` versus `Ætherling`.



Controlled normalization of `Æ` to `Ae` recovered three records that the

historical spreadsheet workflow did not reconcile.



\### Tarmogoyf Pricing Defect



The reconstruction also identified a historical pricing anomaly involving

Tarmogoyf.



Trader Tools contained:



\- Modern Masters: `$139.97`

\- Modern Masters 2015 Edition: `$134.97`



The historical Processing worksheet assigned the Modern Masters record a

`My Price` of:



`$274.94`



The relationship was reproduced directly:



`$139.97 + $134.97 = $274.94`



This demonstrates that both Masters-edition pricing records contributed to the

historical result.



The precise historical spreadsheet formula responsible is not inferred without

direct formula evidence. The Python implementation prevents the condition by

requiring an explicit normalized `Name + Edition` relationship.



\## Repository Structure



```text

tcgplayer-reconciliation-pricing/

├── data/

│   ├── raw\_examples/

│   ├── reconstruction\_inputs/

│   └── reference\_outputs/

├── notebooks/

│   └── 01\_reconciliation\_reconstruction\_reconstituted.ipynb

├── original\_files/

├── outputs/

│   ├── reconciliation/

│   │   └── modernized\_reconciliation\_output.csv

│   └── exceptions/

│       └── reconciliation\_exceptions.csv

├── src/

│   └── reconciliation.py

├── manifest.csv

├── README.md

└── requirements.txt

