
import quart 
import logging 

from client import Client, Resource

import var

app = quart.Quart(__name__)
client = Client()

logging.getLogger('quart.serving').setLevel(logging.ERROR)

if var.production == False:
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.config["TEMPLATES_AUTO_RELOAD"] = True

@app.route("/", methods=["GET"])
async def _index():
    return quart.redirect("/resources")

@app.route("/resources", methods=["GET"])
async def _resources():
    return await quart.render_template("resources.html")

@app.route("/resources/download/<self_id>")
async def _resources_download(self_id):
    resource : Resource = client.caches.ResourceCache.get_by_id(self_id)

    return quart.redirect(await resource.get_download_url(client))

@app.route("/api/resources/extra/<self_id>")
async def _resources_extra(self_id):
    resource : Resource = client.caches.ResourceCache.get_by_id(self_id)
    if not resource.extra_data:
        await resource.fetch_extra_data(client)
    
    return quart.jsonify(resource.to_dict())

@app.route("/api/resources/search")
async def _api_resources_search():
    q = quart.request.args.get("q")

    rs = await client.resources.search(q)
    
    
    return quart.jsonify([r.to_dict() for r in rs])

app.run(host="0.0.0.0", port=var.port, use_reloader=False)

