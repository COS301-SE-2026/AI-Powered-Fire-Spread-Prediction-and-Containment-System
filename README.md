# Repository Coverage (integration)

[Full report](https://htmlpreview.github.io/?https://github.com/COS301-SE-2026/AI-Powered-Fire-Spread-Prediction-and-Containment-System/blob/python-coverage-comment-action-data-integration/htmlcov/index.html)

| Name                                                             |    Stmts |     Miss |   Branch |   BrPart |   Cover |   Missing |
|----------------------------------------------------------------- | -------: | -------: | -------: | -------: | ------: | --------: |
| app/backend/db.py                                                |       30 |       15 |        2 |        0 |     47% |29-36, 46-57 |
| app/backend/main.py                                              |       64 |       10 |        8 |        4 |     81% |40, 43, 47, 52-54, 71, 102, 110, 115 |
| app/backend/ml/features/fuel\_load.py                            |      137 |       18 |       26 |       10 |     82% |85-90, 113, 167-182, 196, 219, 237-\>239, 285-\>300, 304-\>310, 321, 331, 336 |
| app/backend/ml/features/geo\_utils.py                            |       14 |        0 |        2 |        0 |    100% |           |
| app/backend/ml/features/normalization.py                         |       41 |        3 |        0 |        0 |     93% |     43-45 |
| app/backend/ml/features/terrain.py                               |       25 |        0 |        0 |        0 |    100% |           |
| app/backend/ml/features/weather\_grid\_loader.py                 |       33 |       25 |        6 |        0 |     21% |13-15, 22-55 |
| app/backend/ml/models/conv\_lstm.py                              |       41 |        2 |       14 |        4 |     89% |22, 36, 39-\>42, 56-\>60 |
| app/backend/ml/models/conv\_lstm\_cell.py                        |       26 |        0 |        0 |        0 |    100% |           |
| app/backend/ml/models/nowcast\_model.py                          |       27 |        0 |        2 |        1 |     97% | 34-\>exit |
| app/backend/src/ai/artifact\_store.py                            |       61 |       45 |       14 |        0 |     21% |21-24, 31-43, 47-50, 59-81, 91-97, 103-114, 118-121 |
| app/backend/src/ai/cache.py                                      |       89 |        0 |       12 |        0 |    100% |           |
| app/backend/src/ai/dca.py                                        |       51 |        0 |       16 |        2 |     97% |120-\>123, 125-\>128 |
| app/backend/src/ai/features.py                                   |       54 |       47 |       20 |        0 |      9% |13-20, 44-81, 96-110 |
| app/backend/src/ai/geo.py                                        |       16 |        1 |        2 |        1 |     89% |        50 |
| app/backend/src/ai/ignition.py                                   |       29 |       17 |        2 |        0 |     39% |20-22, 30-47, 60-66 |
| app/backend/src/ai/job\_builder.py                               |       97 |        0 |       14 |        0 |    100% |           |
| app/backend/src/ai/model\_pipeline.py                            |       84 |        2 |       12 |        2 |     96% |    31, 67 |
| app/backend/src/ai/resolve\_tiles.py                             |       57 |        0 |       10 |        0 |    100% |           |
| app/backend/src/ai/schema.py                                     |        8 |        0 |        0 |        0 |    100% |           |
| app/backend/src/ai/sim\_constants.py                             |        6 |        0 |        0 |        0 |    100% |           |
| app/backend/src/ai/simulation.py                                 |       95 |        0 |       22 |        0 |    100% |           |
| app/backend/src/ai/simulation\_api.py                            |      324 |       33 |       66 |        5 |     89% |192-218, 277-286, 344, 349, 471, 740-\>752 |
| app/backend/src/ai/suggest\_containment.py                       |      175 |        8 |       42 |        8 |     93% |46, 85, 93, 186, 231, 237, 244, 248 |
| app/backend/src/dependencies/auth.py                             |       78 |       15 |       20 |        4 |     79% |39, 57, 62-63, 84-85, 89, 119-128 |
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
| app/backend/src/models/audit\_log.py                             |       13 |       13 |        0 |        0 |      0% |      1-27 |
| app/backend/src/models/containment\_lines.py                     |       13 |        0 |        0 |        0 |    100% |           |
| app/backend/src/models/notification.py                           |       21 |        0 |        0 |        0 |    100% |           |
| app/backend/src/models/reported\_fires.py                        |       40 |        1 |        2 |        1 |     95% |        79 |
| app/backend/src/models/role\_request.py                          |       20 |        0 |        0 |        0 |    100% |           |
| app/backend/src/models/saved\_location.py                        |       14 |        0 |        0 |        0 |    100% |           |
| app/backend/src/models/users.py                                  |       26 |        0 |        0 |        0 |    100% |           |
| app/backend/src/models/water\_resource.py                        |       24 |        0 |        0 |        0 |    100% |           |
| app/backend/src/models/workers.py                                |       28 |        0 |        0 |        0 |    100% |           |
| app/backend/src/routes/admin/admin\_dashboard.py                 |       15 |        4 |        0 |        0 |     73% |     26-29 |
| app/backend/src/routes/admin/analytics.py                        |       16 |        4 |        0 |        0 |     75% |     26-29 |
| app/backend/src/routes/admin/fire\_reports.py                    |       28 |        3 |        0 |        0 |     89% |30, 35, 42 |
| app/backend/src/routes/admin/role\_requests.py                   |       62 |        6 |        6 |        0 |     91% |34, 122-127 |
| app/backend/src/routes/auth/edit\_password.py                    |       17 |        5 |        0 |        0 |     71% |     17-21 |
| app/backend/src/routes/auth/forgot\_password.py                  |       21 |       10 |        2 |        0 |     48% |21-27, 33-38 |
| app/backend/src/routes/auth/login.py                             |       24 |        5 |        2 |        1 |     77% |31-32, 37-47, 55 |
| app/backend/src/routes/auth/logout.py                            |        6 |        2 |        0 |        0 |     67% |       8-9 |
| app/backend/src/routes/auth/register.py                          |       13 |        2 |        0 |        0 |     85% |     15-16 |
| app/backend/src/routes/auth/two\_factor.py                       |       30 |       10 |        0 |        0 |     67% |22-25, 57-72 |
| app/backend/src/routes/auth/two\_factor\_toggle.py               |       22 |        6 |        0 |        0 |     73% | 23, 27-31 |
| app/backend/src/routes/firefighter/fire\_reports.py              |       28 |       12 |        0 |        0 |     57% |28-29, 39-44, 54-59 |
| app/backend/src/routes/firefighter/fire\_terrain\_bias.py        |       10 |        2 |        0 |        0 |     80% |     19-20 |
| app/backend/src/routes/firefighter/firefighter\_dashboard.py     |       50 |       16 |        0 |        0 |     68% |36-37, 75-78, 86-89, 97-100, 112-113 |
| app/backend/src/routes/geo/water\_bodies.py                      |      107 |       35 |       28 |        7 |     63% |59-74, 100, 121-\>134, 136-156, 184, 187, 197-201, 206-211, 216-217 |
| app/backend/src/routes/guests/fire\_reports.py                   |       14 |        2 |        0 |        0 |     86% |     33-36 |
| app/backend/src/routes/guests/guests\_dashboard.py               |       13 |        5 |        0 |        0 |     62% |     24-28 |
| app/backend/src/routes/guests/nearby\_fires.py                   |       10 |        0 |        0 |        0 |    100% |           |
| app/backend/src/routes/image\_uploads.py                         |       16 |        7 |        0 |        0 |     56% |     24-31 |
| app/backend/src/routes/location.py                               |       17 |        5 |        0 |        0 |     71% |     23-30 |
| app/backend/src/routes/notifications.py                          |       60 |       14 |        6 |        2 |     73% |48-69, 82-85, 90-91, 130-131, 141-142 |
| app/backend/src/routes/resources.py                              |       13 |        0 |        0 |        0 |    100% |           |
| app/backend/src/routes/users/fire\_reports.py                    |       24 |        1 |        0 |        0 |     96% |        55 |
| app/backend/src/routes/users/profile.py                          |       26 |        0 |        2 |        0 |    100% |           |
| app/backend/src/routes/users/resources.py                        |       21 |        2 |        0 |        0 |     90% |    43, 52 |
| app/backend/src/routes/users/role\_request.py                    |       23 |        9 |        2 |        0 |     56% |17, 22-25, 29-33 |
| app/backend/src/routes/users/saved\_location.py                  |       35 |        0 |        0 |        0 |    100% |           |
| app/backend/src/routes/workers.py                                |      289 |       41 |       66 |       13 |     84% |55-56, 62-65, 104-105, 270-\>275, 272-\>275, 276-277, 299, 333-\>335, 347-\>350, 352-\>356, 359-\>323, 370-\>374, 386-389, 403-404, 412-414, 418-420, 434-435, 442-444, 485-495, 501-502 |
| app/backend/src/schemas/admin\_analytics.py                      |        5 |        0 |        0 |        0 |    100% |           |
| app/backend/src/schemas/admin\_dashboard.py                      |        7 |        0 |        0 |        0 |    100% |           |
| app/backend/src/schemas/audit\_log.py                            |        9 |        9 |        0 |        0 |      0% |      1-19 |
| app/backend/src/schemas/auth.py                                  |       28 |        0 |        0 |        0 |    100% |           |
| app/backend/src/schemas/containment\_lines.py                    |       10 |        0 |        0 |        0 |    100% |           |
| app/backend/src/schemas/edit\_password.py                        |        2 |        0 |        0 |        0 |    100% |           |
| app/backend/src/schemas/fire\_report.py                          |       29 |        0 |        0 |        0 |    100% |           |
| app/backend/src/schemas/fire\_terrain\_bias.py                   |        3 |        0 |        0 |        0 |    100% |           |
| app/backend/src/schemas/firefighter\_dashboard.py                |       11 |        0 |        0 |        0 |    100% |           |
| app/backend/src/schemas/firefighter\_reports.py                  |       25 |        0 |        0 |        0 |    100% |           |
| app/backend/src/schemas/fuel\_conditions.py                      |        7 |        0 |        0 |        0 |    100% |           |
| app/backend/src/schemas/notification.py                          |       10 |        0 |        0 |        0 |    100% |           |
| app/backend/src/schemas/push.py                                  |        3 |        0 |        0 |        0 |    100% |           |
| app/backend/src/schemas/resource.py                              |       93 |        8 |       34 |        8 |     87% |60, 67, 71, 83, 100, 102, 104, 114 |
| app/backend/src/schemas/role\_request.py                         |       23 |        0 |        0 |        0 |    100% |           |
| app/backend/src/schemas/saved\_locations.py                      |       14 |        0 |        0 |        0 |    100% |           |
| app/backend/src/schemas/two\_factor\_toggle.py                   |        4 |        0 |        0 |        0 |    100% |           |
| app/backend/src/schemas/user.py                                  |       13 |        0 |        0 |        0 |    100% |           |
| app/backend/src/schemas/user\_location.py                        |        4 |        0 |        0 |        0 |    100% |           |
| app/backend/src/schemas/workers.py                               |       39 |        0 |        0 |        0 |    100% |           |
| app/backend/src/services/admin/analytics\_service.py             |       30 |       17 |        8 |        0 |     34% |17-38, 47-79, 83 |
| app/backend/src/services/admin/dashboard\_service.py             |       71 |       55 |       26 |        0 |     16% |14-19, 25-48, 52-67, 75-78, 81-124, 128-143, 147-154, 158 |
| app/backend/src/services/admin/role\_request.py                  |       74 |        3 |       20 |        0 |     97% |    89-101 |
| app/backend/src/services/auth/edit\_password.py                  |       13 |        8 |        6 |        0 |     26% |      8-16 |
| app/backend/src/services/auth/email.py                           |       33 |       11 |        2 |        0 |     63% |18-34, 37-46 |
| app/backend/src/services/auth/forgot\_password.py                |       51 |       32 |       14 |        0 |     29% |26, 29, 32-50, 53-74 |
| app/backend/src/services/auth/login.py                           |       61 |       13 |       12 |        5 |     75% |44-46, 53-54, 70-73, 80-81, 114-122 |
| app/backend/src/services/auth/pending\_registration.py           |       26 |        3 |        0 |        0 |     88% | 36-38, 41 |
| app/backend/src/services/auth/register.py                        |       13 |        1 |        2 |        1 |     87% |        16 |
| app/backend/src/services/auth/two\_factor.py                     |       49 |       26 |       14 |        1 |     44% |18-32, 45, 64-107 |
| app/backend/src/services/auth/two\_factor\_toggle.py             |        7 |        4 |        2 |        0 |     33% |       6-9 |
| app/backend/src/services/cache.py                                |        9 |        2 |        0 |        0 |     78% |     18-19 |
| app/backend/src/services/fire\_growth.py                         |       13 |        0 |        2 |        0 |    100% |           |
| app/backend/src/services/firefighter/containment\_lines.py       |       76 |       14 |       12 |        4 |     77% |34-36, 56, 69, 92, 109-119, 141-147, 168 |
| app/backend/src/services/firefighter/fire\_merge.py              |       75 |       11 |       20 |        4 |     84% |46, 54-55, 59, 62-63, 73-74, 81, 118-119 |
| app/backend/src/services/firefighter/fire\_terrain\_bias.py      |      115 |       13 |       14 |        5 |     86% |40-41, 45, 51-59, 63, 76-77, 112-113, 149 |
| app/backend/src/services/firefighter/firefighter\_dashboard.py   |       39 |       18 |       12 |        1 |     43% |17-39, 59-60 |
| app/backend/src/services/firefighter/firefighter\_reports.py     |       28 |       11 |        6 |        0 |     56% |42-78, 82-89 |
| app/backend/src/services/firefighter/fuel\_conditions.py         |      135 |      107 |       40 |        0 |     16% |16-22, 25-30, 33-46, 49, 69, 78-93, 100-114, 117-120, 123-126, 134-138, 141-163, 169-270 |
| app/backend/src/services/guests/guests\_dashboard.py             |       39 |       28 |       12 |        0 |     22% |17-32, 38-77 |
| app/backend/src/services/notifications/geo.py                    |       15 |        0 |        2 |        0 |    100% |           |
| app/backend/src/services/notifications/notifications.py          |      181 |       13 |       62 |        9 |     91% |73-80, 82-\>98, 87-94, 99-\>exit, 120, 187, 285, 337, 362, 375-376 |
| app/backend/src/services/notifications/proximity\_scheduler.py   |       21 |       11 |        0 |        0 |     48% |26-31, 38-43 |
| app/backend/src/services/notifications/push\_webpush.py          |       43 |        4 |        8 |        2 |     88% | 58, 89-95 |
| app/backend/src/services/notifications/severity.py               |       14 |        2 |        6 |        2 |     80% |    21, 23 |
| app/backend/src/services/notifications/websocket\_manager.py     |       44 |        7 |       12 |        4 |     77% |45-\>47, 47-\>exit, 53, 60-61, 64-66, 69 |
| app/backend/src/services/resources.py                            |       22 |        0 |        6 |        1 |     96% |   32-\>34 |
| app/backend/src/services/simulation\_service.py                  |        0 |        0 |        0 |        0 |    100% |           |
| app/backend/src/services/storage.py                              |       44 |       17 |       12 |        2 |     55% |19, 35-40, 44-47, 52-55, 62, 73 |
| app/backend/src/services/users/cache.py                          |        9 |        9 |        0 |        0 |      0% |      1-19 |
| app/backend/src/services/users/fire\_report.py                   |       73 |       15 |       22 |        2 |     76% |36, 173-195, 225-\>228 |
| app/backend/src/services/users/profile.py                        |       29 |        6 |        8 |        0 |     84% |     28-33 |
| app/backend/src/services/users/resource.py                       |       42 |       14 |        6 |        0 |     62% |81-96, 100-116 |
| app/backend/src/services/users/role\_request.py                  |       24 |       16 |        4 |        0 |     29% |9-26, 29-30, 33-40 |
| app/backend/src/services/users/saved\_location.py                |       52 |        0 |       14 |        3 |     95% |94-\>96, 96-\>98, 98-\>105 |
| app/backend/src/services/verification/auto\_verification.py      |       29 |        2 |       10 |        2 |     90% |    49, 53 |
| app/backend/src/services/verification/photo\_hashing.py          |        3 |        1 |        0 |        0 |     67% |         8 |
| app/backend/src/services/verification/register\_verification.py  |       35 |       12 |       16 |        5 |     67% |6, 12, 23-24, 27, 31, 45, 56-60 |
| app/backend/src/services/verification/rejection\_checks.py       |       92 |       23 |       30 |       10 |     73% |54, 57-59, 77-92, 98, 117, 151, 156, 161, 165, 167, 169, 173-175 |
| app/backend/src/services/verification/report\_corroboration.py   |       18 |        0 |        0 |        0 |    100% |           |
| app/backend/src/services/verification/report\_spam\_detection.py |       21 |        1 |        4 |        1 |     92% |        18 |
| app/backend/src/services/verification/reporter\_trust.py         |       34 |        5 |       14 |        2 |     81% | 31, 55-59 |
| app/backend/src/services/verification/verification\_runner.py    |       41 |       22 |       12 |        2 |     40% |29, 40-65, 69-70 |
| app/backend/src/services/workers.py                              |      131 |       23 |       38 |       13 |     78% |39, 43, 79-82, 93, 99, 105, 123, 135, 157, 163, 169, 210, 212, 269-275 |
| app/backend/startup\_migrations.py                               |       18 |       18 |        0 |        0 |      0% |      3-97 |
| **TOTAL**                                                        | **5299** | **1096** |  **976** |  **154** | **76%** |           |


## Setup coverage badge

Below are examples of the badges you can use in your main branch `README` file.

### Direct image

[![Coverage badge](https://raw.githubusercontent.com/COS301-SE-2026/AI-Powered-Fire-Spread-Prediction-and-Containment-System/python-coverage-comment-action-data-integration/badge.svg)](https://htmlpreview.github.io/?https://github.com/COS301-SE-2026/AI-Powered-Fire-Spread-Prediction-and-Containment-System/blob/python-coverage-comment-action-data-integration/htmlcov/index.html)

This is the one to use if your repository is private or if you don't want to customize anything.

### [Shields.io](https://shields.io) Json Endpoint

[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/COS301-SE-2026/AI-Powered-Fire-Spread-Prediction-and-Containment-System/python-coverage-comment-action-data-integration/endpoint.json)](https://htmlpreview.github.io/?https://github.com/COS301-SE-2026/AI-Powered-Fire-Spread-Prediction-and-Containment-System/blob/python-coverage-comment-action-data-integration/htmlcov/index.html)

Using this one will allow you to [customize](https://shields.io/endpoint) the look of your badge.
It won't work with private repositories. It won't be refreshed more than once per five minutes.

### [Shields.io](https://shields.io) Dynamic Badge

[![Coverage badge](https://img.shields.io/badge/dynamic/json?color=brightgreen&label=coverage&query=%24.message&url=https%3A%2F%2Fraw.githubusercontent.com%2FCOS301-SE-2026%2FAI-Powered-Fire-Spread-Prediction-and-Containment-System%2Fpython-coverage-comment-action-data-integration%2Fendpoint.json)](https://htmlpreview.github.io/?https://github.com/COS301-SE-2026/AI-Powered-Fire-Spread-Prediction-and-Containment-System/blob/python-coverage-comment-action-data-integration/htmlcov/index.html)

This one will always be the same color. It won't work for private repos. I'm not even sure why we included it.

## What is that?

This branch is part of the
[python-coverage-comment-action](https://github.com/marketplace/actions/python-coverage-comment)
GitHub Action. All the files in this branch are automatically generated and may be
overwritten at any moment.