## Theme candidates — 2026-09-10

Anchors: 62 themes; threshold 0.3 (by source: {'default': 0.3, 'exchange': 0.3, 'mdna': 0.4}) (held-out P 0.302 / R 0.38 on 1725 labelled chunks).
Coverage: question register: 1452/3527 mapped (41%); evidence register: 6061/13589 mapped (45%); by source: exchange source: 5903/11830 mapped (50%), mdna source: 1610/5286 mapped (30%); 5347 rows skipped (operator/untyped speakers, acknowledgements, housekeeping).
A unit maps when its cosine to a theme centroid clears the threshold; the rest are clustered and only clusters with >= 3 companies and >= 2 banks are listed. The system never edits `config/watchlist.yaml` — accept with `topic_map.py --accept <id> --name <slug>`, reject with `--reject <id>`.

### Pending candidates (2 of 41; 0 evidence-only listed below)

| id | suggested | n_banks | n_companies | n_exch | first_seen | tickers | phrases |
|---|---|---|---|---|---|---|---|
| `cand:3355431-t_3355431-t_qna_28_0` | china_margin_disconnect | 4 | 3 | 4 | 2025-12-02 | AMAT, ASML, LRCX | gross margin; china; margins; follow-up; july |
| `cand:3405694-t_qna_62_0` | sales_cycle_lengthening | 3 | 3 | 3 | 2026-03-05 | AXON, GWRE, HNGE | pipeline; longer; half; driving; sales |

#### `cand:3355431-t_3355431-t_qna_28_0` — china_margin_disconnect
_Analysts probing whether margin strength reflects operational leverage or stems from geographic mix shift reducing China exposure._
Banks: Cantor Fitzgerald & Co., JPMorgan Securities LLC, UBS Securities LLC, Wolfe Research LLC
- **AMAT 2025-12-02** (UBS Securities LLC): And that kind of dovetails into gross margin, which I wanted to talk about. That's been a real bright spot. I mean, at similar China portion of revenue in July of 2022, gross margin was 46.2% and you're guiding it to 48.5% with a similar contribution from China. So, if you try to
- **ASML 2026-01-28** (Wolfe Research LLC): My follow-up question is with regard to gross margins, and you spoke about that a bit. But perhaps you could clarify what are the headwinds and tailwinds with respect to gross margin for this year. I presume that China is one factor. But what are the factors that cause you to be 
- **AMAT 2026-05-14** (Cantor Fitzgerald & Co.): As a quick follow-up, just on the gross margin side, great guide with, I'm assuming, depressed China. How should we think about gross margins beyond the July quarter, particularly as it appears as silicon will continue to grow sequentially well into 2027 and beyond?

#### `cand:3405694-t_qna_62_0` — sales_cycle_lengthening
_Pipelines are building strongly but conversions are back-half weighted, indicating sales cycles are extending as enterprise deal sizes and product complexity increase._
Banks: Raymond James & Associates, Inc., WR Securities LLC, William Blair & Co. LLC
- **GWRE 2026-03-05** (William Blair & Co. LLC): I know there's a lot of commentary of the pipeline in the back half of the year, but just wanted to touch on maybe how should we think about the different products flowing through the funnel as customers increasingly want to land larger with longer duration? Has there been any sh
- **HNGE 2026-08-04** (Raymond James & Associates, Inc.): So I wanted to clarify on the selling season, it seems like this is the second year in a row where there's been really strong pipeline build, but the conversion is going to be back half weighted. Is that the new normal that we should expect? And do you think there's anything that
- **AXON 2026-08-05** (WR Securities LLC): In the past, you've talked about longer sales cycles for AI and OSP bundles. With the bigger price tags on those. Are those cycles shortening now that the products have been in the market for longer periods of time, customers might be more familiar, more used to AI or are you kin

### Decided
- `cand:3362309-t_qna_18_0` accepted as `capacity_supply_tightness`
- `cand:3363278-t_qna_60_0` accepted as `pricing_power_in_shortage`
- `cand:3359603-t_3359603-t_qna_14_0` accepted as `capacity_supply_tightness`
- `cand:3438469-t_qna_33_0` accepted as `server_cpu_agentic_tam`
- `cand:3388411-t_qna_10_0` accepted as `neocloud_demand`
- `cand:3354107-t_qna_41_0` accepted as `capacity_supply_tightness`
- `cand:3328815-t_qna_49_0` accepted as `capacity_supply_tightness`
- `cand:3453466-t_3453466-t_qna_68_1` rejected
- `cand:3384162-t_qna_32_0` rejected
- `cand:3433453-t_md_5_4` accepted as `physical_ai_adoption`
- `cand:3381168-t_qna_36_0` rejected
- `cand:3335314-t_3335314-t_qna_22_0` rejected
- `cand:3374273-t_3374273-t_qna_72_0` accepted as `advanced_packaging_substrate_supply`
- `cand:3335314-t_3335314-t_qna_33_0` accepted as `advanced_packaging_substrate_supply`
- `cand:3489856-t_qna_53_0` rejected
- `cand:3505197-t_qna_16_0` rejected
- `cand:3469126-t_qna_53_1` rejected
- `cand:3297800-t_3297800-t_qna_63_0` rejected
- `cand:3366595-t_qna_16_0` accepted as `optical_speed_transition_1_6t`
- `cand:3355794-t_3355794-t_qna_16_0` accepted as `co_packaged_optics_ramp`
- `cand:3355795-t_3355795-t_qna_27_0` accepted as `laser_architecture_competition`
- `cand:3463943-t_qna_23_0` rejected
- `cand:3384540-t_3384540-t_qna_28_0` rejected
- `cand:3385303-t_qna_20_0` accepted as `capacity_supply_tightness`
- `cand:3500983-t_qna_62_0` accepted as `pricing_power_in_shortage`
- `cand:3398918-t_3398918-t_qna_23_0` accepted as `co_packaged_optics_ramp`
- `cand:3397579-t_qna_17_1` rejected
- `cand:3403970-t_qna_21_0` accepted as `capacity_supply_tightness`
- `cand:3384540-t_3384540-t_qna_29_1` accepted as `pricing_power_in_shortage`
- `cand:3450442-t_qna_65_0` rejected
- `cand:3452572-t_qna_50_0` rejected
- `cand:3385152-t_3385152-t_qna_18_0` rejected
- `cand:3359603-t_3359603-t_qna_9_0` rejected
- `cand:3376441-t_qna_38_0` rejected
- `cand:3386656-t_qna_9_1` accepted as `capacity_supply_tightness`
- `cand:3438469-t_qna_59_0` accepted as `server_cpu_agentic_tam`
- `cand:3383478-t_qna_32_0` rejected
- `cand:3404809-t_qna_55_0` accepted as `capacity_supply_tightness`
- `cand:3413799-t_3413799-t_qna_27_0` accepted as `long_term_supply_agreements`
