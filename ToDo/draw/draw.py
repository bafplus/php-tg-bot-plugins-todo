import asyncio, aiohttp, io, logging, time

import urllib

import plugins

logger = logging.getLogger(__name__)


class StaticMapsApi:
    def __init__(self):
        self.api_url = "https://maps.googleapis.com/maps/api/staticmap"
        self.params = {
            "key": "",
            "size": "800x800",
            "scale": "2",
            "maptype ": "roadmap",
            "markers": "",
            "path ": ""
        }

    def initialise(self, bot):
        self.params["key"] = bot.config.get_by_path(['draw.api_key'])
        if not self.params["key"]:
            logger.error("No API key provided for draw plugin. Use /bot config set draw.api_key \"<key>\" to set it.")

    @asyncio.coroutine
    def get_map(self, bot, event, points):
        logger.info("Fetching points {}".format(points))

        self.params["markers"] = points
        self.params["path"] = points

        image_link = "{}?{}".format(self.api_url, urllib.parse.urlencode(self.params))

        logger.info("getting map {}".format(image_link))

        filename = event.conv_id + ".map." + str(time.time()) +".png"
        logger.debug("temporary image file: {}".format(filename))

        r = yield from aiohttp.request('get', image_link)
        raw = yield from r.read()
        image_data = io.BytesIO(raw)
        image_id = yield from bot._client.upload_image(image_data, filename=filename)

        yield from bot.coro_send_message(event.conv.id_, None, image_id=image_id)


_maps = StaticMapsApi()


def _initialise(bot):
    plugins.register_user_command(["draw"])
    _maps.initialise(bot)


def draw(bot, event, *args):
    """Draw line between points"""
    if not _maps.params["key"]:
        return

    points = "|".join(args)
    if not points:
        yield from bot.coro_send_message(event.conv, "Nothing to draw")
    else:
        yield from _maps.get_map(bot, event, points)


