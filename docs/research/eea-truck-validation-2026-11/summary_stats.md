# HDEV vs certified: summary statistics (Job 3)

Error = (HDEV grid-side kWh/km - certified kWh/km) / certified, in %. 
Each run has two CdxA corners (low/high edge); the point error below uses 
the mid of the two corners. 'in range' = certified falls between the low and 
high CdxA HDEV values.

## Per variant (all runs)

| variant | n | median % | 10th % | 90th % | within +/-5% | within +/-10% | certified in CdxA range |
|---|---|---|---|---|---|---|---|
| V-A | 1274 | -26.0 | -68.5 | 0.4 | 6% | 13% | 7% |
| V-B | 1274 | -14.9 | -52.4 | 18.5 | 15% | 25% | 13% |
| V-C | 1274 | -14.3 | -45.0 | 22.4 | 16% | 27% | 16% |
| V-D | 1274 | -18.5 | -61.3 | 25.3 | 12% | 27% | 13% |

## Median % error by architecture

| architecture | V-A | V-B | V-C | V-D |
|---|---|---|---|---|
| E-IEPC | -27.8 (n=466) | -21.6 (n=466) | -10.4 (n=466) | -22.2 (n=466) |
| E-IEPC-wheel | -17.5 (n=342) | 0.5 (n=342) | 2.1 (n=342) | -6.1 (n=342) |
| E2 | -37.0 (n=344) | -30.6 (n=344) | -39.0 (n=344) | -22.2 (n=344) |
| E3 | -19.5 (n=122) | -7.3 (n=122) | -13.2 (n=122) | 26.5 (n=122) |

## Median % error by mission

| mission | V-A | V-B | V-C | V-D |
|---|---|---|---|---|
| Construction | -30.8 (n=190) | -16.3 (n=190) | -5.3 (n=190) | -21.6 (n=190) |
| Long Haul | -26.5 (n=208) | -24.4 (n=208) | -20.5 (n=208) | -15.8 (n=208) |
| Long Haul EMS | -21.9 (n=124) | -12.2 (n=124) | -9.5 (n=124) | -23.9 (n=124) |
| Municipal Utility | -73.2 (n=124) | -67.8 (n=124) | -70.3 (n=124) | -64.0 (n=124) |
| Regional Delivery | -15.9 (n=279) | -10.5 (n=279) | -11.8 (n=279) | 1.5 (n=279) |
| Regional Delivery EMS | -22.0 (n=124) | -11.3 (n=124) | -6.3 (n=124) | -24.4 (n=124) |
| Urban Delivery | -34.3 (n=225) | -10.6 (n=225) | -14.0 (n=225) | -14.6 (n=225) |

## Median % error by component certification method

| component certification method | V-A | V-B | V-C | V-D |
|---|---|---|---|---|
| measured | -18.4 (n=532) | -2.3 (n=532) | 0.0 (n=532) | -7.3 (n=532) |
| standard | -35.0 (n=742) | -28.7 (n=742) | -30.9 (n=742) | -21.2 (n=742) |

## Flags

- no driver failures or skipped runs.
- runs on vehicles with >=1 axle missing RRC/cert-number: 0
