# Tablet Dataset Sources (2020-2025)

This folder now uses the original three-table layout:

1. `tablet_models_2020_2025.csv`
2. `tablet_perf_2020_2025.csv`
3. `tablet_market_2020_2025.csv`

## Source scope

Only three source families were used:

1. DeviceSpecifications
2. Geekbench Browser
3. Canalys Newsroom / Omdia-hosted Canalys press releases

## What each file contains

- `tablet_models_2020_2025.csv`
  - Representative tablet models for Apple, Samsung, Lenovo, Huawei, Xiaomi, Honor, Oppo and Amazon.
  - Fields focus on assignment-relevant specs: form factor, screen, camera and chip.
- `tablet_perf_2020_2025.csv`
  - Geekbench 6 single-core and multi-core reference scores.
  - Where a clean tablet-specific result was not consistently available, a same-SoC Geekbench Browser proxy was used.
- `tablet_market_2020_2025.csv`
  - Continuous quarterly brand-level market table from 2020 Q1 to 2025 Q2.
  - Rows are top vendors reported by Canalys in each quarter plus `Others` and `Total`.

## Important caveats

- DeviceSpecifications pages sometimes expose the same model through language-specific URLs; the CSV stores the normalized data rather than every page variant.
- Camera megapixels in the model table are derived from the listed native resolution:
  - `4032 x 3024` -> about `12.2 MP`
  - `4160 x 3120` -> about `13.0 MP`
  - `3264 x 2448` -> about `8.0 MP`
  - `2560 x 1920` -> about `4.9 MP`
  - `3260 x 2144` -> about `7.0 MP`
  - `8120 x 6180` -> about `50.2 MP`
- Canalys shipment data are brand-level sell-in shipments, not single-model sales.
- Some quarters required using the prior-year comparison columns from later Canalys reports to reconstruct a continuous quarterly series.

## Representative source entry points

- DeviceSpecifications: https://www.devicespecifications.com/
- Geekbench Browser: https://browser.geekbench.com/
- Canalys Q1 2021 tablet market: https://www.canalys.com/newsroom/canalys-global-pc-q1-2021
- Canalys Q2 2021 tablet market: https://www.canalys.com/newsroom/worldwide-pc-market-q2-2021
- Canalys Q1 2022 tablet market: https://www.canalys.com/newsroom/worldwide-tablet-shipments-Q1-2022
- Canalys Q3 2022 tablet market: https://canalys.com/newsroom/worldwide-tablet-and-chromebook-shipments-Q3-2022
- Canalys Q2 2023 tablet market: https://www.canalys.com/newsroom/global-tablet-market-share-Q2-2023
- Canalys Q3 2023 tablet market: https://www.canalys.com/newsroom/global-tablet-shipments-Q3-2023
- Canalys Q4 2023 tablet market: https://canalys.com/newsroom/global-tablet-market-q4-2023
- Canalys Q1 2024 tablet market: https://www.canalys.com/newsroom/global-tablet-market-Q1-2024
- Canalys Q2 2024 tablet market: https://www.canalys.com/newsroom/global-tablet-shipments-Q2-2024
- Canalys Q3 2024 tablet market: https://www.canalys.com/newsroom/worldwide-tablet-shipments-q3-2024
- Canalys Q4 2024 tablet market: https://canalys.com/newsroom/global-tablet-shipments-q4-2024
- Canalys Q1 2025 tablet market: https://canalys.com/newsroom/worldwide-tablet-market-q1-2025
- Canalys Q2 2025 tablet market: https://canalys.com/newsroom/global-tablet-market-q2-2025
