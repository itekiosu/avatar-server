from quart import Quart, send_file, Response
from cmyui import AsyncSQLPool
from utils import uleb128Encode, pack, binary_write, replay_time
import os
import glob
import struct
import hashlib
import data as dataTypes

app = Quart(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 1

dir = '/home/iteki/gulag/.data/avatars'
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

@app.route("/<int:id>")
async def avatar(id):
    if os.path.isfile(f"{dir}/{id}.png"):
        file = id
    else:
        file = "default"
    
    return await send_file(f"{dir}/{file}.png")

@app.route("/replay/<mode>/<int:id>")
async def dl_replay(id, mode):
    replay = await build_replay(id, mode)
    file = Response(replay)
    file.headers["Content-type"] = "application/octet-stream"
    file.headers["Content-length"] = len(replay)
    file.headers["Content-Description"] = "File Transfer"
    file.headers["Content-Disposition"] = f"attachment; filename={id}.osr"
    return file

if __name__ == '__main__':
    app.run()