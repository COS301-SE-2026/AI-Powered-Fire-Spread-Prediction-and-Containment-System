# Repository Coverage (integration)

[Full report](https://htmlpreview.github.io/?https://github.com/COS301-SE-2026/AI-Powered-Fire-Spread-Prediction-and-Containment-System/blob/python-coverage-comment-action-data-integration/htmlcov/index.html)

| Name                                                             |    Stmts |     Miss |   Branch |   BrPart |   Cover |   Missing |
|----------------------------------------------------------------- | -------: | -------: | -------: | -------: | ------: | --------: |
| app/backend/\_\_init\_\_.py                                      |        0 |        0 |        0 |        0 |    100% |           |
| app/backend/db.py                                                |       30 |       15 |        2 |        0 |     47% |29-36, 46-57 |
| app/backend/main.py                                              |       64 |        9 |        8 |        4 |     82% |40, 43, 47, 52-54, 71, 102, 110 |
| app/backend/ml/features/fuel\_load.py                            |      137 |       61 |       26 |        4 |     50% |85-90, 113, 167-182, 196, 219, 236-239, 261-338 |
| app/backend/ml/features/geo\_utils.py                            |       14 |        1 |        2 |        1 |     88% |        34 |
| app/backend/ml/features/normalization.py                         |       41 |        5 |        0 |        0 |     88% |20, 43-45, 52 |
| app/backend/ml/features/terrain.py                               |       25 |        0 |        0 |        0 |    100% |           |
| app/backend/ml/features/weather\_grid\_loader.py                 |       33 |       25 |        6 |        0 |     21% |13-15, 22-55 |
| app/backend/ml/models/conv\_lstm.py                              |       41 |        2 |       14 |        4 |     89% |22, 36, 39-\>42, 56-\>60 |
| app/backend/ml/models/conv\_lstm\_cell.py                        |       26 |        0 |        0 |        0 |    100% |           |
| app/backend/ml/models/nowcast\_model.py                          |       27 |        0 |        2 |        1 |     97% | 34-\>exit |
| app/backend/ml/training/\_\_init\_\_.py                          |        0 |        0 |        0 |        0 |    100% |           |
| app/backend/ml/training/dataset.py                               |       83 |       17 |       16 |        2 |     75% |40-43, 55, 157-177 |
| app/backend/ml/training/losses.py                                |        9 |        0 |        0 |        0 |    100% |           |
| app/backend/ml/training/metrics.py                               |       33 |        0 |        8 |        0 |    100% |           |
| app/backend/ml/training/synthetic\_data.py                       |       60 |        1 |       10 |        2 |     96% |102-\>100, 126 |
| app/backend/ml/training/train\_convlstm.py                       |      201 |       36 |       24 |        4 |     80% |56, 261-266, 276, 335-397, 401 |
| app/backend/ml/training/train\_ignition.py                       |       61 |       24 |       10 |        1 |     59% |32-35, 103-157, 168 |
| app/backend/src/\_\_init\_\_.py                                  |        0 |        0 |        0 |        0 |    100% |           |
| app/backend/src/ai/\_\_init\_\_.py                               |        0 |        0 |        0 |        0 |    100% |           |
| app/backend/src/ai/artifact\_store.py                            |       61 |        6 |       14 |        5 |     83% |38-39, 93, 104-\>111, 107, 113, 120 |
| app/backend/src/ai/build\_ignition\_dataset.py                   |      242 |      242 |       40 |        0 |      0% |     3-563 |
| app/backend/src/ai/build\_training\_manifest.py                  |       91 |       91 |       18 |        0 |      0% |     1-220 |
| app/backend/src/ai/cache.py                                      |       89 |       49 |       12 |        2 |     46% |43, 48-\>39, 50-51, 67-84, 89-105, 111-138, 175-190, 194-221 |
| app/backend/src/ai/dca.py                                        |       51 |       51 |       16 |        0 |      0% |     1-130 |
| app/backend/src/ai/features.py                                   |       54 |        0 |       20 |        0 |    100% |           |
| app/backend/src/ai/geo.py                                        |       16 |        1 |        2 |        1 |     89% |        50 |
| app/backend/src/ai/ignition.py                                   |       29 |        0 |        2 |        0 |    100% |           |
| app/backend/src/ai/inspect\_fire.py                              |       33 |       33 |        6 |        0 |      0% |      1-84 |
| app/backend/src/ai/job\_builder.py                               |       55 |       34 |        6 |        0 |     34% |46-88, 96-127, 151 |
| app/backend/src/ai/model\_pipeline.py                            |       84 |       84 |       12 |        0 |      0% |     1-179 |
| app/backend/src/ai/resolve\_tiles.py                             |       57 |       39 |       10 |        0 |     27% |36-41, 50-59, 78-116, 138-148 |
| app/backend/src/ai/schema.py                                     |        8 |        0 |        0 |        0 |    100% |           |
| app/backend/src/ai/sim\_constants.py                             |        6 |        0 |        0 |        0 |    100% |           |
| app/backend/src/ai/simulation.py                                 |       95 |       75 |       22 |        0 |     17% |17-30, 36-42, 69-82, 91-100, 110-137, 145-149, 154-158, 172-212 |
| app/backend/src/ai/simulation\_api.py                            |      323 |      142 |       66 |        7 |     50% |72-73, 76, 80, 97-98, 177, 191-217, 220-222, 234-269, 276-285, 310-403, 470, 551-631, 655-685, 707-759 |
| app/backend/src/ai/suggest\_containment.py                       |      147 |        7 |       22 |        7 |     92% |44, 78, 86, 184, 188, 195, 199 |
| app/backend/src/dependencies/\_\_init\_\_.py                     |        0 |        0 |        0 |        0 |    100% |           |
| app/backend/src/dependencies/auth.py                             |       78 |       21 |       20 |        4 |     70% |25-26, 31, 39, 57, 62-63, 84-85, 89, 119-128, 133-138 |
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
| app/backend/src/models/reported\_fires.py                        |       40 |        1 |        2 |        1 |     95% |        79 |
| app/backend/src/models/role\_request.py                          |       20 |        0 |        0 |        0 |    100% |           |
| app/backend/src/models/saved\_location.py                        |       14 |        0 |        0 |        0 |    100% |           |
| app/backend/src/models/users.py                                  |       26 |        0 |        0 |        0 |    100% |           |
| app/backend/src/models/water\_resource.py                        |       24 |        0 |        0 |        0 |    100% |           |
| app/backend/src/models/workers.py                                |       28 |        0 |        0 |        0 |    100% |           |
| app/backend/src/routes/\_\_init\_\_.py                           |        8 |        0 |        0 |        0 |    100% |           |
| app/backend/src/routes/admin/\_\_init\_\_.py                     |       10 |        0 |        0 |        0 |    100% |           |
| app/backend/src/routes/admin/admin\_dashboard.py                 |       15 |        4 |        0 |        0 |     73% |     26-29 |
| app/backend/src/routes/admin/analytics.py                        |       16 |        4 |        0 |        0 |     75% |     26-29 |
| app/backend/src/routes/admin/fire\_reports.py                    |       28 |        3 |        0 |        0 |     89% |30, 35, 42 |
| app/backend/src/routes/admin/role\_requests.py                   |       48 |        5 |        6 |        0 |     91% |     76-81 |
| app/backend/src/routes/auth/\_\_init\_\_.py                      |       14 |        0 |        0 |        0 |    100% |           |
| app/backend/src/routes/auth/edit\_password.py                    |       17 |        5 |        0 |        0 |     71% |     17-21 |
| app/backend/src/routes/auth/forgot\_password.py                  |       21 |       10 |        2 |        0 |     48% |21-27, 33-38 |
| app/backend/src/routes/auth/login.py                             |       24 |       11 |        2 |        0 |     50% | 27-47, 55 |
| app/backend/src/routes/auth/logout.py                            |        6 |        2 |        0 |        0 |     67% |       8-9 |
| app/backend/src/routes/auth/register.py                          |       13 |        5 |        0 |        0 |     62% |     13-19 |
| app/backend/src/routes/auth/two\_factor.py                       |       30 |       16 |        0 |        0 |     47% |22-25, 34-49, 57-72 |
| app/backend/src/routes/auth/two\_factor\_toggle.py               |       22 |        6 |        0 |        0 |     73% | 23, 27-31 |
| app/backend/src/routes/firefighter/\_\_init\_\_.py               |        8 |        0 |        0 |        0 |    100% |           |
| app/backend/src/routes/firefighter/fire\_reports.py              |       28 |       12 |        0 |        0 |     57% |28-29, 39-44, 54-59 |
| app/backend/src/routes/firefighter/fire\_terrain\_bias.py        |       10 |        2 |        0 |        0 |     80% |     19-20 |
| app/backend/src/routes/firefighter/firefighter\_dashboard.py     |       50 |       16 |        0 |        0 |     68% |36-37, 75-78, 86-89, 97-100, 112-113 |
| app/backend/src/routes/geo/\_\_init\_\_.py                       |        0 |        0 |        0 |        0 |    100% |           |
| app/backend/src/routes/geo/water\_bodies.py                      |       88 |       25 |       24 |        5 |     66% |57-72, 112-\>125, 127-147, 175, 178, 186-187, 195-196 |
| app/backend/src/routes/guests/\_\_init\_\_.py                    |        8 |        0 |        0 |        0 |    100% |           |
| app/backend/src/routes/guests/fire\_reports.py                   |       14 |        2 |        0 |        0 |     86% |     33-36 |
| app/backend/src/routes/guests/guests\_dashboard.py               |       13 |        5 |        0 |        0 |     62% |     24-28 |
| app/backend/src/routes/guests/nearby\_fires.py                   |       10 |        0 |        0 |        0 |    100% |           |
| app/backend/src/routes/image\_uploads.py                         |       16 |        7 |        0 |        0 |     56% |     24-31 |
| app/backend/src/routes/location.py                               |       17 |        5 |        0 |        0 |     71% |     23-30 |
| app/backend/src/routes/notifications.py                          |       60 |       14 |        6 |        2 |     73% |48-69, 82-85, 90-91, 130-131, 141-142 |
| app/backend/src/routes/resources.py                              |       13 |        0 |        0 |        0 |    100% |           |
| app/backend/src/routes/users/\_\_init\_\_.py                     |       12 |        0 |        0 |        0 |    100% |           |
| app/backend/src/routes/users/fire\_reports.py                    |       24 |        1 |        0 |        0 |     96% |        55 |
| app/backend/src/routes/users/profile.py                          |       27 |        9 |        2 |        0 |     62% |21, 29, 37-43 |
| app/backend/src/routes/users/resources.py                        |       21 |        2 |        0 |        0 |     90% |    43, 52 |
| app/backend/src/routes/users/role\_request.py                    |       23 |        9 |        2 |        0 |     56% |17, 22-25, 29-33 |
| app/backend/src/routes/users/saved\_location.py                  |       35 |       18 |        0 |        0 |     49% |16, 20-23, 31-34, 43-46, 50-54 |
| app/backend/src/routes/workers.py                                |      289 |       41 |       66 |       13 |     84% |55-56, 62-65, 104-105, 270-\>275, 272-\>275, 276-277, 299, 333-\>335, 347-\>350, 352-\>356, 359-\>323, 370-\>374, 386-389, 403-404, 412-414, 418-420, 434-435, 442-444, 485-495, 501-502 |
| app/backend/src/schemas/\_\_init\_\_.py                          |        0 |        0 |        0 |        0 |    100% |           |
| app/backend/src/schemas/admin\_analytics.py                      |        5 |        0 |        0 |        0 |    100% |           |
| app/backend/src/schemas/admin\_dashboard.py                      |        7 |        0 |        0 |        0 |    100% |           |
| app/backend/src/schemas/audit\_log.py                            |        9 |        9 |        0 |        0 |      0% |      1-19 |
| app/backend/src/schemas/auth.py                                  |       28 |        1 |        0 |        0 |     96% |        20 |
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
| app/backend/src/services/\_\_init\_\_.py                         |        0 |        0 |        0 |        0 |    100% |           |
| app/backend/src/services/admin/\_\_init\_\_.py                   |        0 |        0 |        0 |        0 |    100% |           |
| app/backend/src/services/admin/analytics\_service.py             |       30 |       17 |        8 |        0 |     34% |17-38, 47-79, 83 |
| app/backend/src/services/admin/dashboard\_service.py             |       66 |       51 |       24 |        0 |     17% |14-19, 25-48, 52-67, 76-118, 122-137, 141-148, 152 |
| app/backend/src/services/admin/role\_request.py                  |       74 |        3 |       20 |        0 |     97% |    89-101 |
| app/backend/src/services/auth/\_\_init\_\_.py                    |        0 |        0 |        0 |        0 |    100% |           |
| app/backend/src/services/auth/edit\_password.py                  |       13 |        8 |        6 |        0 |     26% |      8-16 |
| app/backend/src/services/auth/email.py                           |       20 |       11 |        2 |        0 |     41% |17-33, 36-45 |
| app/backend/src/services/auth/forgot\_password.py                |       51 |       32 |       14 |        0 |     29% |26, 29, 32-50, 53-74 |
| app/backend/src/services/auth/login.py                           |       61 |       41 |       12 |        0 |     27% |34, 39-54, 62-86, 92-95, 100-122 |
| app/backend/src/services/auth/pending\_registration.py           |       26 |       12 |        0 |        0 |     54% |18, 22-33, 36-38, 41 |
| app/backend/src/services/auth/register.py                        |       13 |        4 |        2 |        0 |     60% |     14-18 |
| app/backend/src/services/auth/two\_factor.py                     |       49 |       35 |       14 |        0 |     22% |18-32, 35-60, 64-107 |
| app/backend/src/services/auth/two\_factor\_toggle.py             |        7 |        4 |        2 |        0 |     33% |       6-9 |
| app/backend/src/services/cache.py                                |        9 |        2 |        0 |        0 |     78% |     18-19 |
| app/backend/src/services/fire\_growth.py                         |       13 |        0 |        2 |        0 |    100% |           |
| app/backend/src/services/firefighter/\_\_init\_\_.py             |        0 |        0 |        0 |        0 |    100% |           |
| app/backend/src/services/firefighter/containment\_lines.py       |       62 |       11 |       12 |        4 |     77% |28-30, 50, 63, 86, 103-113, 134 |
| app/backend/src/services/firefighter/fire\_merge.py              |       75 |       11 |       20 |        4 |     84% |46, 54-55, 59, 62-63, 73-74, 81, 118-119 |
| app/backend/src/services/firefighter/fire\_terrain\_bias.py      |      115 |       13 |       14 |        5 |     86% |40-41, 45, 51-59, 63, 76-77, 112-113, 149 |
| app/backend/src/services/firefighter/firefighter\_dashboard.py   |       39 |       18 |       12 |        1 |     43% |17-39, 59-60 |
| app/backend/src/services/firefighter/firefighter\_reports.py     |       28 |       11 |        6 |        0 |     56% |42-78, 82-89 |
| app/backend/src/services/firefighter/fuel\_conditions.py         |      135 |      107 |       40 |        0 |     16% |16-22, 25-30, 33-46, 49, 69, 78-93, 100-114, 117-120, 123-126, 134-138, 141-163, 169-270 |
| app/backend/src/services/guests/\_\_init\_\_.py                  |        0 |        0 |        0 |        0 |    100% |           |
| app/backend/src/services/guests/guests\_dashboard.py             |       39 |       28 |       12 |        0 |     22% |17-32, 38-77 |
| app/backend/src/services/notifications/\_\_init\_\_.py           |        2 |        0 |        0 |        0 |    100% |           |
| app/backend/src/services/notifications/geo.py                    |       15 |        0 |        2 |        0 |    100% |           |
| app/backend/src/services/notifications/notifications.py          |      181 |       13 |       62 |        9 |     91% |73-80, 82-\>98, 87-94, 99-\>exit, 120, 187, 285, 337, 362, 375-376 |
| app/backend/src/services/notifications/proximity\_scheduler.py   |       21 |       11 |        0 |        0 |     48% |26-31, 38-43 |
| app/backend/src/services/notifications/push\_webpush.py          |       43 |        4 |        8 |        2 |     88% | 58, 89-95 |
| app/backend/src/services/notifications/severity.py               |       14 |        2 |        6 |        2 |     80% |    21, 23 |
| app/backend/src/services/notifications/websocket\_manager.py     |       44 |        7 |       12 |        4 |     77% |45-\>47, 47-\>exit, 53, 60-61, 64-66, 69 |
| app/backend/src/services/resources.py                            |       22 |        0 |        6 |        1 |     96% |   32-\>34 |
| app/backend/src/services/simulation\_service.py                  |        0 |        0 |        0 |        0 |    100% |           |
| app/backend/src/services/storage.py                              |       44 |       17 |       12 |        2 |     55% |19, 35-40, 44-47, 52-55, 62, 73 |
| app/backend/src/services/users/\_\_init\_\_.py                   |        0 |        0 |        0 |        0 |    100% |           |
| app/backend/src/services/users/cache.py                          |        9 |        9 |        0 |        0 |      0% |      1-19 |
| app/backend/src/services/users/fire\_report.py                   |       73 |       16 |       22 |        3 |     74% |36, 90, 173-195, 225-\>228 |
| app/backend/src/services/users/profile.py                        |       17 |       12 |        8 |        0 |     20% |      9-23 |
| app/backend/src/services/users/resource.py                       |       42 |       14 |        6 |        0 |     62% |81-96, 100-116 |
| app/backend/src/services/users/role\_request.py                  |       24 |       16 |        4 |        0 |     29% |9-26, 29-30, 33-40 |
| app/backend/src/services/users/saved\_location.py                |       52 |       37 |       14 |        0 |     23% |19, 29-39, 42-55, 58-80, 83-108, 111-121 |
| app/backend/src/services/verification/\_\_init\_\_.py            |        0 |        0 |        0 |        0 |    100% |           |
| app/backend/src/services/verification/auto\_verification.py      |       29 |        2 |       10 |        2 |     90% |    49, 53 |
| app/backend/src/services/verification/photo\_hashing.py          |        3 |        1 |        0 |        0 |     67% |         8 |
| app/backend/src/services/verification/register\_verification.py  |       35 |       32 |       16 |        0 |      6% |5-47, 56-60 |
| app/backend/src/services/verification/rejection\_checks.py       |       92 |       23 |       30 |       10 |     73% |54, 57-59, 77-92, 98, 117, 151, 156, 161, 165, 167, 169, 173-175 |
| app/backend/src/services/verification/report\_corroboration.py   |       18 |        0 |        0 |        0 |    100% |           |
| app/backend/src/services/verification/report\_spam\_detection.py |       21 |        1 |        4 |        1 |     92% |        18 |
| app/backend/src/services/verification/reporter\_trust.py         |       34 |        5 |       14 |        2 |     81% | 31, 55-59 |
| app/backend/src/services/verification/verification\_runner.py    |       41 |       22 |       12 |        2 |     40% |29, 40-65, 69-70 |
| app/backend/src/services/workers.py                              |      131 |       23 |       38 |       13 |     78% |39, 43, 78-81, 92, 98, 104, 122, 134, 156, 162, 168, 209, 211, 268-274 |
| app/backend/startup\_migrations.py                               |       18 |       18 |        0 |        0 |      0% |      3-97 |
| **TOTAL**                                                        | **6027** | **2064** | **1074** |  **145** | **62%** |           |


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