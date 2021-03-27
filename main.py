from quart import Quart, send_file, Response
from cmyui import AsyncSQLPool
from utils import uleb128Encode, pack_data, binary_write, replay_time
import os
import glob
import hashlib
import data as dataTypes

app = Quart(__name__)
db = AsyncSQLPool()

async def build_replay(sid, mode):
    await db.connect(glob.config.mysql)
    score = await db.fetch(f'SELECT scores_{mode}.*, users.name FROM scores_{mode} LEFT JOIN users ON scores_{mode}.userid = users.id WHERE scores_{mode}.id = {sid}')
    if score["perfect"] == 1:
        combo_bool = True
    else:
        combo_bool = False
    s = f'{int(score["n100"]) + int(score["n300"])}p{score["n50"]}o{score["ngeki"]}o{score["nkatu"]}t{score["nmiss"]}a{score["map_md5"]}r{score["max_combo"]}e{combo_bool}y{score["name"]}o{score["score"]}u{score["grade"]}{score["mods"]}True'
    hashh = hashlib.md5()
    hashh.update(s.encode("utf-8"))
    nhash = hashh.hexdigest()
    if mode != 'vn':
        moder = f'_{mode}'
    else:
        moder = ''
    f = open(f'{glob.config.replay_path}{moder}/{sid}.osr', 'rb')
    f.seek(0)
    rawReplay = f.read()
    map = await db.fetch(f'SELECT * FROM maps WHERE md5 = "{score["map_md5"]}"')
    name = f'{score["name"]} - {map["artist"]} - {map["title"]} [{map["version"]}]'
    full = binary_write([
        [score["mode"], dataTypes.byte],
        [20150414, dataTypes.uInt32],
        [score["map_md5"], dataTypes.string],
        [score["name"], dataTypes.string],
        [nhash, dataTypes.string],
        [score["n300"], dataTypes.uInt16],
        [score["n100"], dataTypes.uInt16],
        [score["n50"], dataTypes.uInt16],
        [score["ngeki"], dataTypes.uInt16],
        [score["nkatu"], dataTypes.uInt16],
        [score["nmiss"], dataTypes.uInt16],
        [score["score"], dataTypes.uInt32],
        [score["max_combo"], dataTypes.uInt16],
        [score["perfect"], dataTypes.byte],
        [score["mods"], dataTypes.uInt32],
        [0, dataTypes.byte],
        [replay_time(int(score["play_time"])), dataTypes.uInt64],
        [rawReplay, dataTypes.rawReplay],
        [0, dataTypes.uInt32],
        [0, dataTypes.uInt32]
    ])
    return [full, name]

@app.route("/replay/<mode>/<int:id>")
async def dl_replay(id, mode):
    replay_s = await build_replay(id, mode)
    replay = replay_s[0]
    retname = replay_s[1]
    file = Response(replay)
    file.headers["Content-type"] = "application/octet-stream"
    file.headers["Content-length"] = len(replay)
    file.headers["Content-Description"] = "File Transfer"
    file.headers["Content-Disposition"] = f"attachment; filename={retname}.osr"
    return file

if __name__ == '__main__':
    app.run()
