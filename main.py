from quart import Quart, send_file, Response
from cmyui import AsyncSQLPool
from utils import uleb128Encode, pack_data, binary_write, replay_time
import os
import glob
import hashlib
import data as dataTypes

app = Quart(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 1

DIR = '/home/iteki/gulag/.data/avatars'
db = AsyncSQLPool()

async def build_replay(sid: int, mode: str):
    await db.connect(glob.config.mysql)
    score = await db.fetch(
        f"SELECT scores_{mode}.*, users.name FROM scores_{mode}"
        f" LEFT JOIN users ON scores_{mode}.userid = users.id"
        f" WHERE scores_{mode}.id = %s", [sid])

    s = f'{int(score["n100"]) + int(score["n300"])}p{score["n50"]}o{score["ngeki"]}o{score["nkatu"]}t{score["nmiss"]}a{score["map_md5"]}r{score["max_combo"]}e{bool(score["perfect"])}y{score["name"]}o{score["score"]}u{score["grade"]}{score["mods"]}True'
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
    return full

@app.route("/<int:_id>")
async def avatar(_id: int):
    if os.path.isfile(f"{DIR}/{_id}.png"):
        _file = _id
    else:
        _file = "default"
    
    return await send_file(f"{DIR}/{_file}.png")

@app.route("/replay/<str:mode>/<int:_id>")
async def dl_replay(_id: int, mode: str):
    replay = await build_replay(_id, mode)
    _file = Response(replay)
    _file.headers["Content-type"] = "application/octet-stream"
    _file.headers["Content-length"] = len(replay)
    _file.headers["Content-Description"] = "File Transfer"
    _file.headers["Content-Disposition"] = f"attachment; filename={_id}.osr"
    return _file

if __name__ == '__main__':
    app.run()