#!/usr/bin/env python3
"""Merge Fatawa Razviya Jild 8 easy-Urdu tashreeh v4 chunks into jild-08.json.

Reads the 13 chunk files listed in chunks-manifest-v4-jild08.json,
concatenates them in order 01 -> 13, derives start_page = min(pages)
where the field is absent, normalises page markers, validates, and
writes {"masail": [...]} to jild-08.json.

ORDER -- chunk order is the order (no quirk, unlike Jild 1 Part 2):
  The v3 merged file ~/workspace/fatawa-app/content/tashreeh/jild-08.json
  has ID order == concatenation order of the v4 chunks 01..13 (verified
  locally by the coordinator: all 367 ids match the v3 sequence exactly).
  Do NOT sort or reorder. Within each chunk, items keep file order.

NO RENAME QUIRK in Jild 8: the v3 merged file has 367 UNIQUE ids — the
  book numbers no masala twice in this jild (unlike Jild 5, which had
  two masail 263 and two masail 304, and Jild 6, which had two masail
  774). Chunk ids are used exactly as written; the merge asserts
  duplicate-free ids instead of renaming anything.
  NOTE: masala-1163 spans the chunk 01/02 boundary; v3 already
  disambiguates the second part as jild8-masala-1163-p109. That is a
  v3 id, kept exactly — it is NOT a merge rename.

START_PAGE: every one of the 13 v4 chunks carries start_page ==
  min(pages) for all its items (verified by the coordinator). The
  derivation code below stays as a safety net; it is expected to
  derive 0 items.

MARKER NORMALISATION (the only text transformation): page markers, if
  present, are normalised to the single form [safha N] written with the
  Urdu word for page:
  - lenticular-bracket form (U+3010/U+3011 around the Urdu word for
    page + number) -> [safha N]
  - [short form] -> [safha N]
  - [safha N] stays as-is
  Applied to every string field of every item (jawab, sawal, title,
  notes). The 13 v4 chunks contain ZERO markers of any form (verified
  locally), so normalisation is expected to be a no-op here; the code
  stays so the merge is robust and the "none remain" assertions still
  run. No other text is touched and no markers are invented.
  NOTE: the literal lenticular-bracket characters are written here only
  as U+3010/U+3011 escapes, never as literal characters in this file.

VALIDATION (fails loudly on any violation):
  367 items; ID sequence EXACTLY == the v3 merged file's ID sequence
  (embedded below as V3_IDS, copied verbatim from
  ~/workspace/fatawa-app/content/tashreeh/jild-08.json); pages per item
  identical to v3 (embedded as V3_PAGES, same source, verified against
  the v3 file before pushing); 619 unique pages (min 5, max 673);
  volume_ids == {48}; start_page == min(pages) for every item (after
  derivation); zero empty tashreeh_jawab; no lenticular / short markers
  remain; first id jild8-p5, last id jild8-p673.
"""
import json
import os
import re

BASE = os.path.dirname(os.path.abspath(__file__))
MANIFEST = "chunks-manifest-v4-jild08.json"

# Concatenation order: chunk files 01 -> 13, in order.
CHUNK_ORDER = [f"jild-08-chunk-{n:02d}.json" for n in range(1, 14)]

EXPECTED_ITEMS = 367
EXPECTED_PAGES = 619
EXPECTED_MIN_PAGE = 5
EXPECTED_MAX_PAGE = 673
EXPECTED_VOLUME_IDS = {48}
EXPECTED_FIRST_ID = "jild8-p5"
EXPECTED_LAST_ID = "jild8-p673"

# v3 ID sequence, verbatim from content/tashreeh/jild-08.json.
V3_IDS = ['jild8-p5', 'jild8-p9', 'jild8-masala-1115', 'jild8-masala-1116', 'jild8-masala-1117', 'jild8-masala-1118', 'jild8-masala-1122', 'jild8-masala-1123', 'jild8-masala-1124', 'jild8-masala-1125', 'jild8-masala-1126', 'jild8-masala-1127', 'jild8-masala-1128', 'jild8-masala-1129', 'jild8-masala-1130', 'jild8-masala-1131', 'jild8-masala-1132', 'jild8-masala-1133', 'jild8-masala-1134', 'jild8-masala-1138', 'jild8-masala-1139', 'jild8-masala-1140', 'jild8-masala-1141', 'jild8-masala-1142', 'jild8-masala-1144', 'jild8-masala-1145', 'jild8-masala-1146', 'jild8-masala-1147', 'jild8-masala-1148', 'jild8-masala-1149', 'jild8-masala-1150', 'jild8-masala-1151', 'jild8-masala-1152', 'jild8-masala-1153', 'jild8-masala-1154', 'jild8-masala-1155', 'jild8-masala-1156', 'jild8-masala-1157', 'jild8-masala-1158', 'jild8-masala-1159', 'jild8-masala-1160', 'jild8-masala-1161', 'jild8-masala-1162', 'jild8-masala-1163', 'jild8-masala-1163-p109', 'jild8-masala-1165', 'jild8-masala-1166', 'jild8-masala-1167', 'jild8-masala-1168', 'jild8-masala-1169', 'jild8-masala-1170', 'jild8-masala-1171', 'jild8-masala-1172', 'jild8-masala-1173', 'jild8-masala-1174', 'jild8-masala-1175', 'jild8-masala-1176', 'jild8-masala-1177', 'jild8-masala-1178', 'jild8-masala-1179', 'jild8-masala-1180', 'jild8-masala-1181', 'jild8-masala-1185', 'jild8-masala-1186', 'jild8-p134', 'jild8-masala-1187', 'jild8-masala-1188', 'jild8-masala-1189', 'jild8-masala-1190', 'jild8-masala-1191', 'jild8-masala-1192', 'jild8-masala-1193', 'jild8-masala-1194', 'jild8-masala-1195', 'jild8-masala-1196', 'jild8-masala-1197', 'jild8-masala-1198', 'jild8-masala-1199', 'jild8-masala-1200', 'jild8-masala-1201', 'jild8-masala-1202', 'jild8-masala-1203', 'jild8-masala-1204', 'jild8-p159', 'jild8-p162', 'jild8-p163', 'jild8-p164', 'jild8-p165', 'jild8-p167', 'jild8-p168', 'jild8-p172', 'jild8-p177', 'jild8-p178', 'jild8-p179', 'jild8-p180', 'jild8-p181', 'jild8-p183', 'jild8-p185', 'jild8-p186', 'jild8-p191', 'jild8-p192', 'jild8-p196', 'jild8-p197', 'jild8-p209', 'jild8-masala-1234', 'jild8-masala-1235', 'jild8-masala-1236', 'jild8-masala-1237', 'jild8-masala-1238-1239', 'jild8-masala-1240', 'jild8-masala-1241', 'jild8-masala-1242', 'jild8-masala-1243', 'jild8-masala-1243-1245', 'jild8-masala-1246', 'jild8-masala-1247', 'jild8-masala-1248', 'jild8-masala-1249', 'jild8-masala-1249-b', 'jild8-masala-1249-c', 'jild8-masala-1250', 'jild8-masala-1251', 'jild8-masala-1251-b', 'jild8-masala-1251-c', 'jild8-masala-1252', 'jild8-masala-1253-1254', 'jild8-masala-1255', 'jild8-masala-1256', 'jild8-masala-1256-b', 'jild8-masala-1256-c', 'jild8-masala-1257', 'jild8-masala-1258', 'jild8-masala-1259-1263', 'jild8-masala-1264', 'jild8-masala-1265', 'jild8-masala-1266', 'jild8-p259', 'jild8-masala-1267', 'jild8-masala-1268', 'jild8-masala-1269', 'jild8-masala-1270', 'jild8-masala-1271', 'jild8-masala-1272', 'jild8-masala-1273', 'jild8-masala-1274', 'jild8-masala-1275', 'jild8-masala-1276', 'jild8-masala-1277', 'jild8-masala-1278', 'jild8-masala-1279', 'jild8-masala-1280', 'jild8-masala-1282', 'jild8-masala-1283', 'jild8-masala-1290', 'jild8-masala-1291', 'jild8-masala-1292', 'jild8-masala-1293', 'jild8-masala-1294', 'jild8-p309', 'jild8-masala-1295', 'jild8-masala-1296', 'jild8-masala-1297', 'jild8-masala-1298', 'jild8-masala-1299', 'jild8-masala-1300', 'jild8-masala-1301', 'jild8-p317', 'jild8-p319', 'jild8-masala-1302', 'jild8-masala-1303', 'jild8-p324', 'jild8-masala-1304', 'jild8-masala-1305', 'jild8-p329', 'jild8-p331', 'jild8-p333', 'jild8-p335', 'jild8-p337', 'jild8-p339', 'jild8-masala-1306', 'jild8-p343', 'jild8-masala-1309', 'jild8-p346', 'jild8-masala-1310', 'jild8-masala-1311', 'jild8-p349', 'jild8-masala-1316', 'jild8-p352', 'jild8-masala-1317', 'jild8-masala-1318', 'jild8-masala-1319', 'jild8-masala-1320', 'jild8-masala-1321', 'jild8-p357', 'jild8-masala-1322', 'jild8-p359', 'jild8-masala-1323', 'jild8-masala-1324', 'jild8-masala-1325', 'jild8-p365', 'jild8-p367', 'jild8-p369', 'jild8-p373', 'jild8-p376', 'jild8-p379', 'jild8-p382', 'jild8-masala-1329', 'jild8-masala-1330', 'jild8-masala-1331', 'jild8-p387', 'jild8-p389', 'jild8-p391', 'jild8-masala-1334', 'jild8-masala-1335', 'jild8-masala-1336', 'jild8-masala-1337', 'jild8-masala-1338', 'jild8-masala-1339', 'jild8-masala-1340', 'jild8-masala-1341', 'jild8-masala-1344', 'jild8-masala-1345', 'jild8-masala-1346', 'jild8-masala-1347', 'jild8-p409', 'jild8-masala-1348', 'jild8-masala-1349', 'jild8-p417', 'jild8-p420', 'jild8-p423', 'jild8-p425', 'jild8-masala-1350', 'jild8-p428', 'jild8-p432', 'jild8-masala-1352', 'jild8-masala-1353', 'jild8-masala-1354', 'jild8-masala-1355', 'jild8-masala-1356', 'jild8-masala-1357', 'jild8-masala-1358', 'jild8-masala-1359', 'jild8-masala-1360', 'jild8-masala-1361', 'jild8-masala-1362', 'jild8-masala-1363', 'jild8-masala-1364', 'jild8-masala-1365', 'jild8-masala-1366', 'jild8-masala-1367', 'jild8-masala-1368', 'jild8-masala-1369', 'jild8-masala-1370', 'jild8-masala-1371', 'jild8-masala-1372-1376', 'jild8-masala-1377', 'jild8-masala-1378-1381', 'jild8-masala-1382', 'jild8-masala-1384', 'jild8-masala-1384-1385', 'jild8-masala-1386', 'jild8-masala-1387', 'jild8-masala-1388', 'jild8-p459', 'jild8-masala-1389', 'jild8-masala-1390', 'jild8-masala-1392', 'jild8-masala-1395', 'jild8-masala-1396', 'jild8-masala-1397', 'jild8-masala-1398', 'jild8-masala-1399', 'jild8-masala-1400', 'jild8-masala-1401', 'jild8-masala-1404', 'jild8-masala-1405', 'jild8-masala-1406', 'jild8-masala-1407', 'jild8-masala-1408', 'jild8-masala-1409', 'jild8-masala-1410', 'jild8-masala-1411', 'jild8-p509', 'jild8-p510', 'jild8-p512', 'jild8-p514', 'jild8-p517', 'jild8-p519', 'jild8-p522', 'jild8-p524', 'jild8-p526', 'jild8-p529', 'jild8-p532', 'jild8-p534', 'jild8-p536', 'jild8-p540', 'jild8-p542', 'jild8-p544', 'jild8-p548', 'jild8-p550', 'jild8-p552', 'jild8-p554', 'jild8-p556', 'jild8-p559', 'jild8-p561', 'jild8-p563', 'jild8-p567', 'jild8-p569', 'jild8-p571', 'jild8-p572', 'jild8-p576', 'jild8-p577', 'jild8-p581', 'jild8-p583', 'jild8-p584', 'jild8-p585', 'jild8-p586', 'jild8-p588', 'jild8-p590', 'jild8-p593', 'jild8-p594', 'jild8-p596', 'jild8-p597', 'jild8-p599', 'jild8-p600', 'jild8-p602', 'jild8-p604', 'jild8-p606', 'jild8-p609', 'jild8-p612', 'jild8-p615', 'jild8-p617', 'jild8-p620', 'jild8-p622', 'jild8-p624', 'jild8-p625', 'jild8-p628', 'jild8-p631', 'jild8-p634', 'jild8-p635', 'jild8-p637', 'jild8-p639', 'jild8-p641', 'jild8-p642', 'jild8-p644', 'jild8-p646', 'jild8-p648', 'jild8-p650', 'jild8-p652', 'jild8-p654', 'jild8-p656', 'jild8-p658', 'jild8-p659', 'jild8-p660', 'jild8-p661', 'jild8-p662', 'jild8-p663', 'jild8-p664', 'jild8-p665', 'jild8-p666', 'jild8-p667', 'jild8-p668', 'jild8-p669', 'jild8-p670', 'jild8-p671', 'jild8-p672', 'jild8-p673']

# v3 pages per item id, verbatim from content/tashreeh/jild-08.json.
V3_PAGES = {
"jild8-p5": [5, 6, 7],
"jild8-p9": [9, 10, 11, 12, 13, 14, 15, 16, 17],
"jild8-masala-1115": [57],
"jild8-masala-1116": [59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71],
"jild8-masala-1117": [71, 72, 73],
"jild8-masala-1118": [73],
"jild8-masala-1122": [73],
"jild8-masala-1123": [73, 74],
"jild8-masala-1124": [74, 75],
"jild8-masala-1125": [75, 76],
"jild8-masala-1126": [76, 77],
"jild8-masala-1127": [77],
"jild8-masala-1128": [77, 78],
"jild8-masala-1129": [78, 79, 80],
"jild8-masala-1130": [80, 81, 82, 83, 84],
"jild8-masala-1131": [84],
"jild8-masala-1132": [85, 86],
"jild8-masala-1133": [86, 87],
"jild8-masala-1134": [87, 88],
"jild8-masala-1138": [88, 89],
"jild8-masala-1139": [89],
"jild8-masala-1140": [89, 90],
"jild8-masala-1141": [90],
"jild8-masala-1142": [90, 91],
"jild8-masala-1144": [91, 92, 93, 94, 95],
"jild8-masala-1145": [95],
"jild8-masala-1146": [95],
"jild8-masala-1147": [95, 96],
"jild8-masala-1148": [95, 96],
"jild8-masala-1149": [96],
"jild8-masala-1150": [96, 97, 98, 99],
"jild8-masala-1151": [99, 100],
"jild8-masala-1152": [100],
"jild8-masala-1153": [100, 101, 102],
"jild8-masala-1154": [102],
"jild8-masala-1155": [103],
"jild8-masala-1156": [103, 104],
"jild8-masala-1157": [104],
"jild8-masala-1158": [104, 105],
"jild8-masala-1159": [105, 106, 107],
"jild8-masala-1160": [107, 108],
"jild8-masala-1161": [108],
"jild8-masala-1162": [108],
"jild8-masala-1163": [108],
"jild8-masala-1163-p109": [109],
"jild8-masala-1165": [109, 110],
"jild8-masala-1166": [110],
"jild8-masala-1167": [110, 111, 112],
"jild8-masala-1168": [112],
"jild8-masala-1169": [112, 113],
"jild8-masala-1170": [112, 113],
"jild8-masala-1171": [113],
"jild8-masala-1172": [113],
"jild8-masala-1173": [113, 114, 115],
"jild8-masala-1174": [116, 117, 118, 119],
"jild8-masala-1175": [119, 120, 121, 122],
"jild8-masala-1176": [122],
"jild8-masala-1177": [122, 123],
"jild8-masala-1178": [123],
"jild8-masala-1179": [124],
"jild8-masala-1180": [124],
"jild8-masala-1181": [124, 125, 126],
"jild8-masala-1185": [126, 128],
"jild8-masala-1186": [129, 130, 131, 132, 133],
"jild8-p134": [134, 135, 136],
"jild8-masala-1187": [136, 137],
"jild8-masala-1188": [137, 138],
"jild8-masala-1189": [138],
"jild8-masala-1190": [140],
"jild8-masala-1191": [141, 142],
"jild8-masala-1192": [142, 143],
"jild8-masala-1193": [143, 144],
"jild8-masala-1194": [144, 145],
"jild8-masala-1195": [145, 146],
"jild8-masala-1196": [146, 147, 148],
"jild8-masala-1197": [148, 149, 150, 151, 152, 153],
"jild8-masala-1198": [153],
"jild8-masala-1199": [153, 154],
"jild8-masala-1200": [154],
"jild8-masala-1201": [154, 155, 156, 157],
"jild8-masala-1202": [157, 158],
"jild8-masala-1203": [158],
"jild8-masala-1204": [158],
"jild8-p159": [159, 160, 161, 162],
"jild8-p162": [162, 163],
"jild8-p163": [163, 164],
"jild8-p164": [164, 165],
"jild8-p165": [165, 166, 167],
"jild8-p167": [167, 168],
"jild8-p168": [168, 169, 170, 171, 172],
"jild8-p172": [172, 173, 174, 175],
"jild8-p177": [177],
"jild8-p178": [178, 179],
"jild8-p179": [179, 180],
"jild8-p180": [180, 181],
"jild8-p181": [181, 182, 183],
"jild8-p183": [183, 184, 185],
"jild8-p185": [185, 186],
"jild8-p186": [186, 187, 188, 189, 190, 191],
"jild8-p191": [191, 192],
"jild8-p192": [192, 193, 194, 195],
"jild8-p196": [196],
"jild8-p197": [197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207, 208],
"jild8-p209": [209, 210],
"jild8-masala-1234": [210, 211],
"jild8-masala-1235": [212],
"jild8-masala-1236": [212],
"jild8-masala-1237": [212, 213],
"jild8-masala-1238-1239": [213, 214],
"jild8-masala-1240": [214, 215],
"jild8-masala-1241": [214, 215],
"jild8-masala-1242": [215],
"jild8-masala-1243": [215],
"jild8-masala-1243-1245": [216],
"jild8-masala-1246": [216, 217, 218],
"jild8-masala-1247": [220],
"jild8-masala-1248": [220, 221, 222],
"jild8-masala-1249": [223, 224, 225, 226, 227, 228],
"jild8-masala-1249-b": [229, 230, 231, 232],
"jild8-masala-1249-c": [232, 233],
"jild8-masala-1250": [233, 234],
"jild8-masala-1251": [234, 235],
"jild8-masala-1251-b": [235, 236],
"jild8-masala-1251-c": [238, 239],
"jild8-masala-1252": [239],
"jild8-masala-1253-1254": [239, 240],
"jild8-masala-1255": [240],
"jild8-masala-1256": [241, 242],
"jild8-masala-1256-b": [243, 244, 245, 246, 247],
"jild8-masala-1256-c": [247, 248, 249, 250, 251],
"jild8-masala-1257": [251, 252, 253, 254],
"jild8-masala-1258": [254],
"jild8-masala-1259-1263": [254, 255],
"jild8-masala-1264": [255, 256, 257, 258],
"jild8-masala-1265": [258],
"jild8-masala-1266": [258],
"jild8-p259": [259, 260, 261, 262, 263, 264, 265, 266],
"jild8-masala-1267": [267],
"jild8-masala-1268": [267, 268],
"jild8-masala-1269": [268, 269],
"jild8-masala-1270": [268, 269],
"jild8-masala-1271": [270],
"jild8-masala-1272": [270],
"jild8-masala-1273": [270, 271],
"jild8-masala-1274": [271],
"jild8-masala-1275": [271, 272],
"jild8-masala-1276": [273, 274, 275, 276, 277, 278],
"jild8-masala-1277": [278, 279, 280, 281, 282],
"jild8-masala-1278": [282, 283, 284, 285, 286],
"jild8-masala-1279": [286, 287],
"jild8-masala-1280": [287, 288, 289, 290, 291, 292, 293],
"jild8-masala-1282": [293, 294, 295, 296],
"jild8-masala-1283": [296, 297, 298, 299, 300],
"jild8-masala-1290": [300, 301],
"jild8-masala-1291": [301, 302],
"jild8-masala-1292": [302, 303],
"jild8-masala-1293": [303],
"jild8-masala-1294": [303, 304, 305, 306, 307, 308],
"jild8-p309": [309],
"jild8-masala-1295": [309, 310],
"jild8-masala-1296": [310, 311],
"jild8-masala-1297": [312],
"jild8-masala-1298": [312, 313],
"jild8-masala-1299": [313, 314],
"jild8-masala-1300": [314, 315],
"jild8-masala-1301": [315, 316],
"jild8-p317": [317, 318],
"jild8-p319": [319, 320],
"jild8-masala-1302": [320, 321, 322],
"jild8-masala-1303": [322, 323],
"jild8-p324": [324, 325],
"jild8-masala-1304": [326],
"jild8-masala-1305": [327, 328],
"jild8-p329": [329, 330],
"jild8-p331": [331, 332],
"jild8-p333": [333, 334],
"jild8-p335": [335, 336],
"jild8-p337": [337, 338],
"jild8-p339": [339, 340, 341],
"jild8-masala-1306": [341, 342],
"jild8-p343": [343, 344],
"jild8-masala-1309": [344, 345],
"jild8-p346": [346],
"jild8-masala-1310": [346, 347],
"jild8-masala-1311": [347, 348],
"jild8-p349": [349, 350],
"jild8-masala-1316": [350, 351],
"jild8-p352": [352],
"jild8-masala-1317": [352],
"jild8-masala-1318": [352, 353],
"jild8-masala-1319": [354],
"jild8-masala-1320": [354, 355],
"jild8-masala-1321": [355, 356],
"jild8-p357": [357, 358],
"jild8-masala-1322": [358],
"jild8-p359": [359, 360],
"jild8-masala-1323": [361, 362],
"jild8-masala-1324": [362, 363, 364, 365],
"jild8-masala-1325": [365],
"jild8-p365": [365, 366, 367],
"jild8-p367": [367, 368, 369],
"jild8-p369": [369, 370, 371, 372, 373],
"jild8-p373": [373, 374, 375, 376],
"jild8-p376": [376, 377, 378],
"jild8-p379": [379, 380, 381],
"jild8-p382": [382, 383],
"jild8-masala-1329": [384],
"jild8-masala-1330": [384, 385, 386],
"jild8-masala-1331": [386, 387],
"jild8-p387": [387, 388, 389],
"jild8-p389": [389, 390],
"jild8-p391": [391, 392, 393, 394],
"jild8-masala-1334": [394, 395, 396],
"jild8-masala-1335": [396],
"jild8-masala-1336": [396, 397],
"jild8-masala-1337": [397, 398],
"jild8-masala-1338": [398, 399],
"jild8-masala-1339": [399],
"jild8-masala-1340": [399, 400, 401],
"jild8-masala-1341": [401, 402],
"jild8-masala-1344": [402, 403, 404],
"jild8-masala-1345": [404],
"jild8-masala-1346": [404, 405],
"jild8-masala-1347": [405, 406, 407, 408],
"jild8-p409": [409, 410, 411],
"jild8-masala-1348": [411, 412],
"jild8-masala-1349": [413, 414, 415, 416],
"jild8-p417": [417, 418, 419],
"jild8-p420": [420, 421, 422],
"jild8-p423": [423, 424],
"jild8-p425": [425, 426],
"jild8-masala-1350": [426, 427, 428],
"jild8-p428": [428, 429, 430, 431],
"jild8-p432": [432, 433, 434, 435],
"jild8-masala-1352": [436],
"jild8-masala-1353": [436, 437],
"jild8-masala-1354": [438],
"jild8-masala-1355": [438, 439],
"jild8-masala-1356": [439],
"jild8-masala-1357": [439, 440],
"jild8-masala-1358": [440, 441],
"jild8-masala-1359": [441],
"jild8-masala-1360": [441],
"jild8-masala-1361": [441, 442],
"jild8-masala-1362": [442, 443],
"jild8-masala-1363": [443, 444],
"jild8-masala-1364": [444, 445],
"jild8-masala-1365": [445, 446],
"jild8-masala-1366": [446],
"jild8-masala-1367": [446],
"jild8-masala-1368": [447, 448],
"jild8-masala-1369": [449, 450],
"jild8-masala-1370": [450],
"jild8-masala-1371": [450, 451],
"jild8-masala-1372-1376": [451, 452],
"jild8-masala-1377": [452, 453, 454],
"jild8-masala-1378-1381": [454, 455],
"jild8-masala-1382": [455],
"jild8-masala-1384": [456],
"jild8-masala-1384-1385": [456, 457, 458],
"jild8-masala-1386": [458],
"jild8-masala-1387": [458],
"jild8-masala-1388": [458],
"jild8-p459": [459],
"jild8-masala-1389": [459, 460, 461],
"jild8-masala-1390": [461, 462],
"jild8-masala-1392": [462, 463],
"jild8-masala-1395": [463, 464],
"jild8-masala-1396": [464, 465],
"jild8-masala-1397": [465],
"jild8-masala-1398": [465, 466],
"jild8-masala-1399": [466],
"jild8-masala-1400": [466, 467],
"jild8-masala-1401": [467, 468],
"jild8-masala-1404": [468],
"jild8-masala-1405": [469],
"jild8-masala-1406": [469, 470, 471],
"jild8-masala-1407": [471, 472, 474, 475, 476],
"jild8-masala-1408": [477, 479, 480, 481, 482, 483, 484, 485, 486],
"jild8-masala-1409": [486, 487, 488, 489, 490, 491, 492, 493, 495, 496],
"jild8-masala-1410": [496, 497],
"jild8-masala-1411": [498, 499, 500, 501, 502, 503, 504, 505, 507, 508],
"jild8-p509": [509],
"jild8-p510": [510, 511],
"jild8-p512": [512, 513],
"jild8-p514": [514, 515, 516],
"jild8-p517": [517, 518],
"jild8-p519": [519, 520, 521],
"jild8-p522": [522, 523],
"jild8-p524": [524, 525],
"jild8-p526": [526, 527, 528],
"jild8-p529": [529, 530, 531],
"jild8-p532": [532, 533],
"jild8-p534": [534, 535],
"jild8-p536": [536, 537, 538, 539],
"jild8-p540": [540, 541],
"jild8-p542": [542, 543],
"jild8-p544": [544, 545, 546, 547],
"jild8-p548": [548, 549],
"jild8-p550": [550, 551],
"jild8-p552": [552, 553],
"jild8-p554": [554, 555],
"jild8-p556": [556, 557, 558],
"jild8-p559": [559, 560, 561],
"jild8-p561": [561, 562, 563],
"jild8-p563": [563, 564, 565, 566, 567],
"jild8-p567": [567, 568, 569],
"jild8-p569": [569, 570, 571],
"jild8-p571": [571, 572],
"jild8-p572": [572, 573, 574, 575],
"jild8-p576": [576, 577],
"jild8-p577": [577, 578, 579, 580, 581],
"jild8-p581": [581, 582, 583],
"jild8-p583": [583, 584],
"jild8-p584": [584, 585],
"jild8-p585": [585, 586],
"jild8-p586": [586, 587, 588],
"jild8-p588": [588, 589, 590],
"jild8-p590": [590, 591, 592, 593],
"jild8-p593": [593, 594],
"jild8-p594": [594, 595, 596],
"jild8-p596": [596, 597],
"jild8-p597": [597, 598, 599],
"jild8-p599": [599, 600],
"jild8-p600": [600, 601],
"jild8-p602": [602, 603, 604],
"jild8-p604": [604, 605, 606],
"jild8-p606": [606, 607, 608],
"jild8-p609": [609, 610, 611],
"jild8-p612": [612, 613, 614],
"jild8-p615": [615, 616],
"jild8-p617": [617, 618, 619],
"jild8-p620": [620, 621],
"jild8-p622": [622, 623],
"jild8-p624": [624, 625],
"jild8-p625": [626, 627],
"jild8-p628": [628, 629, 630],
"jild8-p631": [631, 632, 633],
"jild8-p634": [634, 635],
"jild8-p635": [635, 636],
"jild8-p637": [637, 638, 639],
"jild8-p639": [639, 640],
"jild8-p641": [641],
"jild8-p642": [642, 643],
"jild8-p644": [644, 645],
"jild8-p646": [646, 647],
"jild8-p648": [648, 649],
"jild8-p650": [650, 651],
"jild8-p652": [652, 653],
"jild8-p654": [654, 655],
"jild8-p656": [656, 657],
"jild8-p658": [658],
"jild8-p659": [659],
"jild8-p660": [660],
"jild8-p661": [661],
"jild8-p662": [662],
"jild8-p663": [663],
"jild8-p664": [664],
"jild8-p665": [665],
"jild8-p666": [666],
"jild8-p667": [667],
"jild8-p668": [668],
"jild8-p669": [669],
"jild8-p670": [670],
"jild8-p671": [671],
"jild8-p672": [672],
"jild8-p673": [673],
}

# The Urdu word for "page" is safha; the canonical marker is [safha N].
# Lenticular brackets are U+3010 (open) and U+3011 (close); the short
# form is "[safha-initial N]" with the single-letter abbreviation.
# All three patterns are built from escapes so this file never contains
# a literal lenticular-bracket pair.
SAFHA = "\u0635\u0641\u062d\u06c1"  # the Urdu word for page
RE_LENTICULAR = re.compile("\u3010" + SAFHA + " (\\d+)\u3011")
RE_SHORT = re.compile("\\[\u0635 (\\d+)\\]")
RE_FULL = re.compile("\\[" + SAFHA + " \\d+\\]")
LENTICULAR_PREFIX = "\u3010" + SAFHA  # for the "none remain" check
SHORT_PREFIX_RE = re.compile("\\[\u0635 \\d+\\]")

# Canonical output key order for every item (the JSON contract).
ITEM_KEYS = ["id", "title", "volume_id", "pages", "start_page",
             "tashreeh_sawal", "tashreeh_jawab", "notes"]


def normalise_markers(text):
    """Normalise page markers in one string. Returns (new_text, counts)."""
    counts = {"lenticular": 0, "short": 0, "full_before": 0}
    counts["full_before"] = len(RE_FULL.findall(text))
    text, n1 = RE_LENTICULAR.subn("[" + SAFHA + " \\1]", text)
    counts["lenticular"] = n1
    text, n2 = RE_SHORT.subn("[" + SAFHA + " \\1]", text)
    counts["short"] = n2
    return text, counts


def normalise_item(item):
    """Normalise markers in every string field of one item (recursively
    through lists/dicts). Returns per-form counts for this item."""
    totals = {"lenticular": 0, "short": 0, "full_before": 0}

    def walk(value):
        if isinstance(value, str):
            new, c = normalise_markers(value)
            for k in totals:
                totals[k] += c[k]
            return new
        if isinstance(value, list):
            return [walk(v) for v in value]
        if isinstance(value, dict):
            return {k: walk(v) for k, v in value.items()}
        return value

    for key in list(item.keys()):
        item[key] = walk(item[key])
    return totals


def main():
    assert len(V3_IDS) == EXPECTED_ITEMS, "embedded V3_IDS length mismatch"
    assert set(V3_PAGES) == set(V3_IDS), "embedded V3_PAGES keys != V3_IDS"
    assert sum(len(v) for v in V3_PAGES.values()) >= EXPECTED_PAGES

    manifest = json.load(open(os.path.join(BASE, MANIFEST), encoding="utf-8"))
    entries = manifest["chunks"]
    assert len(entries) == 13, f"expected 13 manifest entries, got {len(entries)}"
    assert all(e.get("status") == "done" for e in entries), "not all chunks done"
    by_file = {e["file"]: e for e in entries}
    assert set(by_file) == set(CHUNK_ORDER), (
        f"manifest files != CHUNK_ORDER: "
        f"missing={set(CHUNK_ORDER) - set(by_file)} "
        f"extra={set(by_file) - set(CHUNK_ORDER)}"
    )

    all_items = []
    derived = []
    for fname in CHUNK_ORDER:
        path = os.path.join(BASE, fname)
        d = json.load(open(path, encoding="utf-8"))
        items = d["masail"]
        entry = by_file[fname]
        assert len(items) == entry["items"], (
            f"{fname}: {len(items)} items, manifest says {entry['items']}"
        )
        # Marker normalisation, with before/after counts per chunk.
        before = {"lenticular": 0, "short": 0, "full_before": 0}
        for it in items:
            c = normalise_item(it)
            for k in before:
                before[k] += c[k]
        after_full = sum(
            len(RE_FULL.findall(json.dumps(it, ensure_ascii=False)))
            for it in items
        )
        print(
            f"{fname}: {len(items)} items | markers before: "
            f"lenticular={before['lenticular']} short={before['short']} "
            f"full={before['full_before']} | after: full={after_full}"
        )
        assert after_full == (
            before["lenticular"] + before["short"] + before["full_before"]
        ), f"{fname}: marker count changed by normalisation!"
        # Derive start_page = min(pages) where absent (none expected: all chunks carry start_page).
        for it in items:
            if "start_page" not in it:
                it["start_page"] = min(it["pages"])
                derived.append(it["id"])
        all_items.extend(items)

    # NO RENAME QUIRK in Jild 8: the v3 merged file has 367 UNIQUE
    # ids — the book numbers no masala twice in this jild. Chunk ids
    # are used exactly as written.
    assert len(all_items) == len({it["id"] for it in all_items}), (
        f"DUPLICATE IDS before validation: "
        f"{[i for i in [it['id'] for it in all_items] if [it['id'] for it in all_items].count(i) > 1]}"
    )
    print("renames applied: [] (no duplicate masala numbers in Jild 8)")

    print(f"concatenated: {len(all_items)} items")
    print(f"start_page derived for {len(derived)} items (expected 0: all chunks carry start_page)")
    assert len(all_items) == EXPECTED_ITEMS, (
        f"expected {EXPECTED_ITEMS} items, got {len(all_items)}"
    )

    # Rebuild each item in the canonical key order (the JSON contract).
    canonical = []
    for it in all_items:
        assert set(it.keys()) == set(ITEM_KEYS), (
            f"{it.get('id')}: keys {sorted(it.keys())} != {sorted(ITEM_KEYS)}"
        )
        canonical.append({k: it[k] for k in ITEM_KEYS})
    all_items = canonical

    # Validation.
    ids = [it["id"] for it in all_items]
    assert ids == V3_IDS, (
        f"ID sequence != v3: first diff at "
        f"{next((i for i, (a, b) in enumerate(zip(ids, V3_IDS)) if a != b), min(len(ids), len(V3_IDS)))}"
    )
    assert len(ids) == len(set(ids)), (
        f"DUPLICATE IDS: {[i for i in ids if ids.count(i) > 1]}"
    )
    empty = [it["id"] for it in all_items if not it.get("tashreeh_jawab")]
    assert not empty, f"EMPTY JAWAB: {empty}"
    vols = set(it.get("volume_id") for it in all_items)
    assert vols == EXPECTED_VOLUME_IDS, f"volume_ids {vols} != {EXPECTED_VOLUME_IDS}"
    pages = set()
    for it in all_items:
        assert it["pages"] == V3_PAGES[it["id"]], (
            f"{it['id']}: pages {it['pages']} != v3 {V3_PAGES[it['id']]}"
        )
        pages.update(it["pages"])
    assert len(pages) == EXPECTED_PAGES, (
        f"expected {EXPECTED_PAGES} unique pages, got {len(pages)}"
    )
    assert min(pages) == EXPECTED_MIN_PAGE, f"min page {min(pages)}"
    assert max(pages) == EXPECTED_MAX_PAGE, f"max page {max(pages)}"
    exceptions = {
        it["id"] for it in all_items if it["start_page"] != min(it["pages"])
    }
    assert not exceptions, f"start_page != min(pages): {sorted(exceptions)}"
    assert ids[0] == EXPECTED_FIRST_ID, f"first id {ids[0]}"
    assert ids[-1] == EXPECTED_LAST_ID, f"last id {ids[-1]}"

    out = {"masail": all_items}
    out_text = json.dumps(out, ensure_ascii=False, indent=1)
    assert LENTICULAR_PREFIX not in out_text, "lenticular markers remain in output!"
    assert not SHORT_PREFIX_RE.search(out_text), "short markers remain in output!"
    total_markers = len(RE_FULL.findall(out_text))
    print(
        f"VALIDATION PASSED: {len(all_items)} items, {len(pages)} unique pages "
        f"(min {min(pages)}, max {max(pages)}), volume_ids {sorted(vols)}, "
        f"first {ids[0]}, last {ids[-1]}, start_page == min(pages) for all, "
        f"derived start_page for {len(derived)} items, markers {total_markers}"
    )

    with open(os.path.join(BASE, "jild-08.json"), "w", encoding="utf-8") as f:
        f.write(out_text)
    print(f"WROTE jild-08.json: {len(out_text.encode('utf-8'))} bytes")


if __name__ == "__main__":
    main()
