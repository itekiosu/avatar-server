from quart import Quart, send_file
import os

app = Quart(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 1

dir = '/home/iteki/gulag/.data/avatars'

@app.route("/<int:id>")
async def avatar(id):
    if os.path.isfile(f"{dir}/{id}.png"):
        file = id
    else:
        file = "default"
    
    return await send_file(f"{dir}/{file}.png")

if __name__ == '__main__':
    app.run()