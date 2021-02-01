from quart import Quart, send_file
import os

app = Quart(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 1

dir = '/home/iteki/gulag/.data/avatars'
rvn = '/home/iteki/gulag/.data/osr'
rrx = '/home/iteki/gulag/.data/osr_rx'
rap = '/home/iteki/gulag/.data/osr_ap'

@app.route("/<int:id>")
async def avatar(id):
    if os.path.isfile(f"{dir}/{id}.png"):
        file = id
    else:
        file = "default"
    
    return await send_file(f"{dir}/{file}.png")

@app.route("/replay/<int:id>")
async def dl_replay(id):
    if os.path.isfile(f"{rvn}/{id}.osr"):
        file = f'{rvn}/{id}.osr'
        return await send_file(file, as_attachment=True, attachment_filename=f'{id}.osr')
    else:
        e = os.path.isfile(f"{rrx}/{id}.osr")
    
    if e:
        file = f'{rrx}/{id}.osr'
        return await send_file(file, as_attachment=True, attachment_filename=f'{id}.osr')
    else:
        e = os.path.isfile(f"{rap}/{id}.osr")
    
    if e:
        file = f'{rap}/{id}.osr'
        return await send_file(file, as_attachment=True, attachment_filename=f'{id}.osr')
    else:
        return 'Invalid replay ID!'

if __name__ == '__main__':
    app.run()
