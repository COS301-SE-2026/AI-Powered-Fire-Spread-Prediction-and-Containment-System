# Repository Coverage (unit)

[Full report](https://htmlpreview.github.io/?https://github.com/COS301-SE-2026/AI-Powered-Fire-Spread-Prediction-and-Containment-System/blob/python-coverage-comment-action-data-unit/htmlcov/index.html)

| Name                                                             |    Stmts |     Miss |   Branch |   BrPart |   Cover |   Missing |
|----------------------------------------------------------------- | -------: | -------: | -------: | -------: | ------: | --------: |
| app/backend/\_\_init\_\_.py                                      |        0 |        0 |        0 |        0 |    100% |           |
| app/backend/db.py                                                |       30 |       15 |        2 |        0 |     47% |29-36, 46-57 |
| app/backend/main.py                                              |       64 |       18 |        8 |        0 |     64% |35-54, 71, 102, 110, 115 |
| app/backend/ml/features/fuel\_load.py                            |      137 |       95 |       26 |        0 |     26% |83-91, 96-100, 112-129, 139-153, 167-182, 195-220, 236-239, 261-338 |
| app/backend/ml/features/geo\_utils.py                            |       14 |        7 |        2 |        0 |     44% |     31-42 |
| app/backend/ml/features/normalization.py                         |       41 |       18 |        0 |        0 |     56% |16, 20, 25, 28-35, 38-40, 43-45, 48-49, 52 |
| app/backend/ml/features/terrain.py                               |       25 |       15 |        0 |        0 |     40% |28-38, 50-68 |
| app/backend/ml/models/conv\_lstm.py                              |       41 |       34 |       14 |        0 |     13% |19-32, 35-60 |
| app/backend/ml/models/conv\_lstm\_cell.py                        |       26 |       19 |        0 |        0 |     27% |11-16, 27-39, 44-46 |
| app/backend/ml/models/nowcast\_model.py                          |       27 |       12 |        2 |        0 |     52% |21-30, 33-35, 38-41 |
| app/backend/ml/training/\_\_init\_\_.py                          |        0 |        0 |        0 |        0 |    100% |           |
| app/backend/ml/training/dataset.py                               |       83 |        3 |       16 |        1 |     94% |   172-177 |
| app/backend/ml/training/losses.py                                |        9 |        0 |        0 |        0 |    100% |           |
| app/backend/ml/training/metrics.py                               |       32 |        0 |        8 |        0 |    100% |           |
| app/backend/ml/training/train\_convlstm.py                       |      187 |       69 |       24 |        2 |     60% |51, 226-246, 257-274, 285-302, 310-375, 379 |
| app/backend/src/\_\_init\_\_.py                                  |        0 |        0 |        0 |        0 |    100% |           |
| app/backend/src/ai/\_\_init\_\_.py                               |        0 |        0 |        0 |        0 |    100% |           |
| app/backend/src/ai/artifact\_store.py                            |       61 |       45 |       14 |        0 |     21% |21-24, 31-43, 47-50, 59-81, 91-97, 103-114, 118-121 |
| app/backend/src/ai/build\_ignition\_dataset.py                   |      242 |       69 |       40 |        3 |     71% |172, 183, 346-\>361, 373-391, 399, 430-559, 563 |
| app/backend/src/ai/build\_training\_manifest.py                  |       91 |       91 |       18 |        0 |      0% |     1-220 |
| app/backend/src/ai/cache.py                                      |       89 |       70 |       12 |        0 |     19% |28-53, 67-84, 89-105, 111-138, 154-172, 175-190, 194-221 |
| app/backend/src/ai/dca.py                                        |       51 |       42 |       16 |        0 |     13% |    50-130 |
| app/backend/src/ai/features.py                                   |       54 |        0 |       20 |        0 |    100% |           |
| app/backend/src/ai/geo.py                                        |       16 |        4 |        2 |        0 |     67% |     47-52 |
| app/backend/src/ai/ignition.py                                   |       29 |       17 |        2 |        0 |     39% |20-22, 30-47, 60-66 |
| app/backend/src/ai/inspect\_fire.py                              |       33 |       33 |        6 |        0 |      0% |      1-84 |
| app/backend/src/ai/job\_builder.py                               |       51 |       30 |        4 |        0 |     38% |46-83, 91-122, 146 |
| app/backend/src/ai/model\_pipeline.py                            |       39 |       31 |        2 |        0 |     20% |31-109, 127-166 |
| app/backend/src/ai/resolve\_tiles.py                             |       57 |       39 |       10 |        0 |     27% |36-41, 50-59, 78-116, 138-148 |
| app/backend/src/ai/schema.py                                     |        8 |        0 |        0 |        0 |    100% |           |
| app/backend/src/ai/sim\_constants.py                             |        6 |        0 |        0 |        0 |    100% |           |
| app/backend/src/ai/simulation.py                                 |       95 |       65 |       22 |        0 |     27% |17-30, 36-42, 91-100, 110-137, 145-149, 154-158, 172-212 |
| app/backend/src/ai/simulation\_api.py                            |      307 |      187 |       66 |        1 |     36% |71-80, 89-110, 159-163, 174-200, 240-\>exit, 256-279, 293-383, 397-511, 528-608, 632-662, 684-736 |
| app/backend/src/ai/suggest\_containment.py                       |      147 |        7 |       22 |        7 |     92% |44, 78, 86, 184, 188, 195, 199 |
| app/backend/src/dependencies/\_\_init\_\_.py                     |        0 |        0 |        0 |        0 |    100% |           |
| app/backend/src/dependencies/auth.py                             |       78 |       32 |       20 |        4 |     53% |39, 56-63, 68-\>72, 71, 81-91, 115-128, 133-138 |
| app/backend/src/enums/\_\_init\_\_.py                            |        0 |        0 |        0 |        0 |    100% |           |
| app/backend/src/enums/audit\_action.py                           |       18 |       18 |        0 |        0 |      0% |      1-25 |
| app/backend/src/enums/fire\_danger.py                            |        7 |        0 |        0 |        0 |    100% |           |
| app/backend/src/enums/fire\_status.py                            |        6 |        0 |        0 |        0 |    100% |           |
| app/backend/src/enums/notification\_type.py                      |        4 |        0 |        0 |        0 |    100% |           |
| app/backend/src/enums/report\_priority.py                        |        6 |        0 |        0 |        0 |    100% |           |
| app/backend/src/enums/report\_status.py                          |        7 |        0 |        0 |        0 |    100% |           |
| app/backend/src/enums/resource.py                                |       23 |        0 |        4 |        0 |    100% |           |
| app/backend/src/enums/role\_request\_status.py                   |        6 |        0 |        0 |        0 |    100% |           |
| app/backend/src/enums/severity.py                                |        6 |        0 |        0 |        0 |    100% |           |
| app/backend/src/enums/user\_role.py                              |        5 |        0 |        0 |        0 |    100% |           |
| app/backend/src/enums/worker\_status.py                          |        9 |        0 |        0 |        0 |    100% |           |
| app/backend/src/models/\_\_init\_\_.py                           |        0 |        0 |        0 |        0 |    100% |           |
| app/backend/src/models/audit\_log.py                             |       13 |       13 |        0 |        0 |      0% |      1-27 |
| app/backend/src/models/containment\_lines.py                     |       13 |        0 |        0 |        0 |    100% |           |
| app/backend/src/models/notification.py                           |       21 |        0 |        0 |        0 |    100% |           |
| app/backend/src/models/reported\_fires.py                        |       40 |        3 |        2 |        0 |     88% |     77-79 |
| app/backend/src/models/role\_request.py                          |       20 |        0 |        0 |        0 |    100% |           |
| app/backend/src/models/saved\_location.py                        |       14 |        0 |        0 |        0 |    100% |           |
| app/backend/src/models/users.py                                  |       26 |        0 |        0 |        0 |    100% |           |
| app/backend/src/models/water\_resource.py                        |       24 |        0 |        0 |        0 |    100% |           |
| app/backend/src/models/workers.py                                |       28 |        1 |        0 |        0 |     96% |        14 |
| app/backend/src/routes/\_\_init\_\_.py                           |        8 |        0 |        0 |        0 |    100% |           |
| app/backend/src/routes/admin/\_\_init\_\_.py                     |       10 |        0 |        0 |        0 |    100% |           |
| app/backend/src/routes/admin/admin\_dashboard.py                 |       15 |        4 |        0 |        0 |     73% |     26-29 |
| app/backend/src/routes/admin/analytics.py                        |       16 |        4 |        0 |        0 |     75% |     26-29 |
| app/backend/src/routes/admin/fire\_reports.py                    |       28 |        7 |        0 |        0 |     75% |30, 35, 42, 53-56 |
| app/backend/src/routes/admin/role\_requests.py                   |       48 |        2 |        6 |        0 |     96% |     80-81 |
| app/backend/src/routes/auth/\_\_init\_\_.py                      |       10 |        0 |        0 |        0 |    100% |           |
| app/backend/src/routes/auth/forgot\_password.py                  |       21 |       10 |        2 |        0 |     48% |21-27, 33-38 |
| app/backend/src/routes/auth/login.py                             |       24 |       11 |        2 |        0 |     50% | 27-47, 55 |
| app/backend/src/routes/auth/logout.py                            |        6 |        2 |        0 |        0 |     67% |       8-9 |
| app/backend/src/routes/auth/register.py                          |       13 |        5 |        0 |        0 |     62% |     13-19 |
| app/backend/src/routes/auth/two\_factor.py                       |       30 |       16 |        0 |        0 |     47% |22-25, 34-49, 57-72 |
| app/backend/src/routes/firefighter/\_\_init\_\_.py               |        8 |        0 |        0 |        0 |    100% |           |
| app/backend/src/routes/firefighter/fire\_reports.py              |       28 |       15 |        0 |        0 |     46% |24-29, 39-44, 54-59 |
| app/backend/src/routes/firefighter/fire\_terrain\_bias.py        |       10 |        4 |        0 |        0 |     60% |     17-20 |
| app/backend/src/routes/firefighter/firefighter\_dashboard.py     |       50 |       29 |        0 |        0 |     42% |33-47, 63-66, 75-78, 86-89, 97-100, 110-113 |
| app/backend/src/routes/geo/\_\_init\_\_.py                       |        0 |        0 |        0 |        0 |    100% |           |
| app/backend/src/routes/geo/water\_bodies.py                      |       88 |       15 |       24 |        1 |     84% |88-98, 112-\>125, 186-187, 195-196 |
| app/backend/src/routes/guests/\_\_init\_\_.py                    |        8 |        0 |        0 |        0 |    100% |           |
| app/backend/src/routes/guests/fire\_reports.py                   |       14 |        0 |        0 |        0 |    100% |           |
| app/backend/src/routes/guests/guests\_dashboard.py               |       13 |        5 |        0 |        0 |     62% |     24-28 |
| app/backend/src/routes/guests/nearby\_fires.py                   |       10 |        1 |        0 |        0 |     90% |        23 |
| app/backend/src/routes/image\_uploads.py                         |       16 |        7 |        0 |        0 |     56% |     24-31 |
| app/backend/src/routes/location.py                               |       17 |        5 |        0 |        0 |     71% |     23-30 |
| app/backend/src/routes/notifications.py                          |       60 |       34 |        6 |        0 |     39% |48-69, 82-85, 90-91, 101-102, 110-111, 127-151 |
| app/backend/src/routes/resources.py                              |       13 |        0 |        0 |        0 |    100% |           |
| app/backend/src/routes/users/\_\_init\_\_.py                     |       12 |        0 |        0 |        0 |    100% |           |
| app/backend/src/routes/users/fire\_reports.py                    |       24 |        7 |        0 |        0 |     71% |27, 38-48, 55 |
| app/backend/src/routes/users/profile.py                          |       27 |        9 |        2 |        0 |     62% |21, 29, 37-43 |
| app/backend/src/routes/users/resources.py                        |       21 |        3 |        0 |        0 |     86% |34, 43, 52 |
| app/backend/src/routes/users/role\_request.py                    |       23 |        9 |        2 |        0 |     56% |17, 22-25, 29-33 |
| app/backend/src/routes/users/saved\_location.py                  |       35 |       18 |        0 |        0 |     49% |16, 20-23, 31-34, 43-46, 50-54 |
| app/backend/src/routes/workers.py                                |      289 |      230 |       66 |        0 |     17% |46-56, 59-65, 68-69, 72-73, 78-91, 104-105, 115-116, 128-129, 147-148, 168-169, 185, 195, 203-220, 236, 257, 269-404, 408-414, 417-504 |
| app/backend/src/schemas/\_\_init\_\_.py                          |        0 |        0 |        0 |        0 |    100% |           |
| app/backend/src/schemas/admin\_analytics.py                      |        5 |        0 |        0 |        0 |    100% |           |
| app/backend/src/schemas/admin\_dashboard.py                      |        7 |        0 |        0 |        0 |    100% |           |
| app/backend/src/schemas/audit\_log.py                            |        9 |        9 |        0 |        0 |      0% |      1-19 |
| app/backend/src/schemas/auth.py                                  |       28 |        1 |        0 |        0 |     96% |        20 |
| app/backend/src/schemas/containment\_lines.py                    |       10 |        0 |        0 |        0 |    100% |           |
| app/backend/src/schemas/fire\_report.py                          |       29 |        0 |        0 |        0 |    100% |           |
| app/backend/src/schemas/fire\_terrain\_bias.py                   |        3 |        0 |        0 |        0 |    100% |           |
| app/backend/src/schemas/firefighter\_dashboard.py                |       11 |        0 |        0 |        0 |    100% |           |
| app/backend/src/schemas/firefighter\_reports.py                  |       25 |        0 |        0 |        0 |    100% |           |
| app/backend/src/schemas/fuel\_conditions.py                      |        7 |        0 |        0 |        0 |    100% |           |
| app/backend/src/schemas/notification.py                          |       10 |        1 |        0 |        0 |     90% |        28 |
| app/backend/src/schemas/push.py                                  |        3 |        0 |        0 |        0 |    100% |           |
| app/backend/src/schemas/resource.py                              |       93 |        0 |       34 |        0 |    100% |           |
| app/backend/src/schemas/role\_request.py                         |       20 |        0 |        0 |        0 |    100% |           |
| app/backend/src/schemas/saved\_locations.py                      |       14 |        0 |        0 |        0 |    100% |           |
| app/backend/src/schemas/user.py                                  |       13 |        0 |        0 |        0 |    100% |           |
| app/backend/src/schemas/user\_location.py                        |        4 |        0 |        0 |        0 |    100% |           |
| app/backend/src/schemas/workers.py                               |       39 |        0 |        0 |        0 |    100% |           |
| app/backend/src/services/\_\_init\_\_.py                         |        0 |        0 |        0 |        0 |    100% |           |
| app/backend/src/services/admin/\_\_init\_\_.py                   |        0 |        0 |        0 |        0 |    100% |           |
| app/backend/src/services/admin/analytics\_service.py             |       30 |       17 |        8 |        0 |     34% |17-38, 47-79, 83 |
| app/backend/src/services/admin/dashboard\_service.py             |       66 |       51 |       24 |        0 |     17% |14-19, 25-48, 52-67, 76-118, 122-137, 141-148, 152 |
| app/backend/src/services/admin/role\_request.py                  |       61 |        0 |       18 |        0 |    100% |           |
| app/backend/src/services/auth/\_\_init\_\_.py                    |        0 |        0 |        0 |        0 |    100% |           |
| app/backend/src/services/auth/email.py                           |       20 |       11 |        2 |        0 |     41% |17-33, 36-45 |
| app/backend/src/services/auth/forgot\_password.py                |       51 |       32 |       14 |        0 |     29% |26, 29, 32-50, 53-74 |
| app/backend/src/services/auth/login.py                           |       61 |       11 |       12 |        2 |     77% |52-\>exit, 86, 100-122 |
| app/backend/src/services/auth/pending\_registration.py           |       26 |       12 |        0 |        0 |     54% |18, 22-33, 36-38, 41 |
| app/backend/src/services/auth/register.py                        |       13 |        4 |        2 |        0 |     60% |     14-18 |
| app/backend/src/services/auth/two\_factor.py                     |       49 |       35 |       14 |        0 |     22% |18-32, 35-60, 64-107 |
| app/backend/src/services/cache.py                                |        9 |        0 |        0 |        0 |    100% |           |
| app/backend/src/services/fire\_growth.py                         |       13 |        0 |        2 |        0 |    100% |           |
| app/backend/src/services/firefighter/\_\_init\_\_.py             |        0 |        0 |        0 |        0 |    100% |           |
| app/backend/src/services/firefighter/containment\_lines.py       |       62 |       37 |       12 |        0 |     34% |28-30, 36-56, 60-76, 79-100, 103-113, 118-156 |
| app/backend/src/services/firefighter/fire\_merge.py              |       75 |        9 |       20 |        2 |     86% |60-63, 73-74, 121-123 |
| app/backend/src/services/firefighter/fire\_terrain\_bias.py      |      115 |       39 |       14 |        0 |     60% |32-33, 44-59, 62-77, 105-143, 146-149 |
| app/backend/src/services/firefighter/firefighter\_dashboard.py   |       39 |       27 |       12 |        0 |     24% |17-39, 44-71, 75-77 |
| app/backend/src/services/firefighter/firefighter\_reports.py     |       28 |       18 |        6 |        0 |     29% |12-38, 42-78, 82-89 |
| app/backend/src/services/firefighter/fuel\_conditions.py         |      135 |      107 |       40 |        0 |     16% |16-22, 25-30, 33-46, 49, 69, 78-93, 100-114, 117-120, 123-126, 134-138, 141-163, 169-270 |
| app/backend/src/services/guests/\_\_init\_\_.py                  |        0 |        0 |        0 |        0 |    100% |           |
| app/backend/src/services/guests/guests\_dashboard.py             |       39 |       28 |       12 |        0 |     22% |17-32, 38-77 |
| app/backend/src/services/notifications/\_\_init\_\_.py           |        2 |        0 |        0 |        0 |    100% |           |
| app/backend/src/services/notifications/geo.py                    |       15 |        0 |        2 |        0 |    100% |           |
| app/backend/src/services/notifications/notifications.py          |      181 |       23 |       62 |        2 |     86% |57-100, 187, 362 |
| app/backend/src/services/notifications/proximity\_scheduler.py   |       21 |       11 |        0 |        0 |     48% |26-31, 38-43 |
| app/backend/src/services/notifications/push\_webpush.py          |       43 |        0 |        8 |        0 |    100% |           |
| app/backend/src/services/notifications/severity.py               |       14 |        0 |        6 |        0 |    100% |           |
| app/backend/src/services/notifications/websocket\_manager.py     |       44 |       26 |       12 |        0 |     32% |19, 23, 38-40, 43-48, 51-66, 69 |
| app/backend/src/services/resources.py                            |       22 |        2 |        6 |        3 |     82% |32-\>34, 35, 41 |
| app/backend/src/services/simulation\_service.py                  |        0 |        0 |        0 |        0 |    100% |           |
| app/backend/src/services/storage.py                              |       44 |       18 |       12 |        3 |     52% |19, 35-40, 44-47, 52-55, 62, 65, 73 |
| app/backend/src/services/users/\_\_init\_\_.py                   |        0 |        0 |        0 |        0 |    100% |           |
| app/backend/src/services/users/cache.py                          |        9 |        9 |        0 |        0 |      0% |      1-19 |
| app/backend/src/services/users/fire\_report.py                   |       73 |       29 |       22 |        0 |     55% |29-74, 78-93, 173-195 |
| app/backend/src/services/users/profile.py                        |       17 |       12 |        8 |        0 |     20% |      9-23 |
| app/backend/src/services/users/resource.py                       |       42 |       20 |        6 |        0 |     46% |60-78, 81-96, 100-116 |
| app/backend/src/services/users/role\_request.py                  |       24 |       16 |        4 |        0 |     29% |9-26, 29-30, 33-40 |
| app/backend/src/services/users/saved\_location.py                |       52 |       37 |       14 |        0 |     23% |19, 29-39, 42-55, 58-80, 83-108, 111-121 |
| app/backend/src/services/verification/\_\_init\_\_.py            |        0 |        0 |        0 |        0 |    100% |           |
| app/backend/src/services/verification/auto\_verification.py      |       29 |       17 |       10 |        0 |     31% |     32-64 |
| app/backend/src/services/verification/photo\_hashing.py          |        3 |        1 |        0 |        0 |     67% |         8 |
| app/backend/src/services/verification/register\_verification.py  |       35 |       32 |       16 |        0 |      6% |5-47, 56-60 |
| app/backend/src/services/verification/rejection\_checks.py       |       92 |       54 |       30 |        0 |     31% |53-60, 65-67, 72, 97-105, 111-137, 142-145, 150-177 |
| app/backend/src/services/verification/report\_corroboration.py   |       18 |        4 |        0 |        0 |     78% |     28-48 |
| app/backend/src/services/verification/report\_spam\_detection.py |       21 |       12 |        4 |        0 |     36% |17-33, 39-50 |
| app/backend/src/services/verification/reporter\_trust.py         |       15 |        9 |        4 |        0 |     32% |     15-29 |
| app/backend/src/services/verification/verification\_runner.py    |       41 |        3 |       12 |        2 |     91% |29, 62, 70 |
| app/backend/src/services/workers.py                              |      131 |       74 |       38 |        4 |     37% |39, 43, 54-\>56, 77-80, 89-110, 119-143, 153-178, 206-213, 217-218, 222-223, 252-300 |
| app/backend/startup\_migrations.py                               |       18 |       18 |        0 |        0 |      0% |      3-97 |
| **TOTAL**                                                        | **5689** | **2430** | **1016** |   **37** | **53%** |           |


## Setup coverage badge

Below are examples of the badges you can use in your main branch `README` file.

### Direct image

[![Coverage badge](https://raw.githubusercontent.com/COS301-SE-2026/AI-Powered-Fire-Spread-Prediction-and-Containment-System/python-coverage-comment-action-data-unit/badge.svg)](https://htmlpreview.github.io/?https://github.com/COS301-SE-2026/AI-Powered-Fire-Spread-Prediction-and-Containment-System/blob/python-coverage-comment-action-data-unit/htmlcov/index.html)

This is the one to use if your repository is private or if you don't want to customize anything.

### [Shields.io](https://shields.io) Json Endpoint

[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/COS301-SE-2026/AI-Powered-Fire-Spread-Prediction-and-Containment-System/python-coverage-comment-action-data-unit/endpoint.json)](https://htmlpreview.github.io/?https://github.com/COS301-SE-2026/AI-Powered-Fire-Spread-Prediction-and-Containment-System/blob/python-coverage-comment-action-data-unit/htmlcov/index.html)

Using this one will allow you to [customize](https://shields.io/endpoint) the look of your badge.
It won't work with private repositories. It won't be refreshed more than once per five minutes.

### [Shields.io](https://shields.io) Dynamic Badge

[![Coverage badge](https://img.shields.io/badge/dynamic/json?color=brightgreen&label=coverage&query=%24.message&url=https%3A%2F%2Fraw.githubusercontent.com%2FCOS301-SE-2026%2FAI-Powered-Fire-Spread-Prediction-and-Containment-System%2Fpython-coverage-comment-action-data-unit%2Fendpoint.json)](https://htmlpreview.github.io/?https://github.com/COS301-SE-2026/AI-Powered-Fire-Spread-Prediction-and-Containment-System/blob/python-coverage-comment-action-data-unit/htmlcov/index.html)

This one will always be the same color. It won't work for private repos. I'm not even sure why we included it.

## What is that?

This branch is part of the
[python-coverage-comment-action](https://github.com/marketplace/actions/python-coverage-comment)
GitHub Action. All the files in this branch are automatically generated and may be
overwritten at any moment.