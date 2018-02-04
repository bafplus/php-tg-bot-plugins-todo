#Written by agent KillNine. Changes by agent thesolo.
#Dependency on Astral & GeoPy

import pytz
import hangups
import plugins
import geopy
import astral

from astral import Location
from datetime import datetime
from geopy.geocoders import GoogleV3

def _initialise(bot):
    plugins.register_user_command(["sun"])

def sun(bot, event, location=None, depression='civil', *args):

    if not location:
        yield from bot.coro_send_message(event.conv_id, _('No location specified; please enter a location.'))
        return

    if depression not in {'civil', 'nautical', 'astronomical'}:
        yield from bot.coro_send_message(event.conv, "Please set preferred solar depression to one of 'civil', 'nautical', or 'astronomical'. 'Civil' is most commonly used.")
        return

    # Geocode our location, thanks Google
    geo = GoogleV3()
    
    lookup_location = geo.geocode(location)
    tz = geo.timezone(lookup_location.point)
    dt = datetime.utcnow()

    # Construct Astral location based on input and geocoding
    astral_location = Location()
    astral_location.name = lookup_location.address
    astral_location.region = ''
    astral_location.latitude = lookup_location.latitude
    astral_location.longitude = lookup_location.longitude
    astral_location.timezone = str(tz)
    astral_location.solar_depression = depression
    sun = astral_location.sun(dt, local=False)

    segments = [hangups.ChatMessageSegment('Assuming {} depression, today in {} the solar event times are: '.format(depression, astral_location.name), is_bold=True),
                hangups.ChatMessageSegment('\n', hangups.SegmentType.LINE_BREAK),
                hangups.ChatMessageSegment('Dawn: %s' % sun['dawn'].astimezone(tz).strftime('%I:%M %p')),
                hangups.ChatMessageSegment('\n', hangups.SegmentType.LINE_BREAK),
                hangups.ChatMessageSegment('Sunrise: %s' % sun['sunrise'].astimezone(tz).strftime('%I:%M %p')),
                hangups.ChatMessageSegment('\n', hangups.SegmentType.LINE_BREAK),
                hangups.ChatMessageSegment('Noon: %s' % sun['noon'].astimezone(tz).strftime('%I:%M %p')),
                hangups.ChatMessageSegment('\n', hangups.SegmentType.LINE_BREAK),
                hangups.ChatMessageSegment('Sunset: %s' % sun['sunset'].astimezone(tz).strftime('%I:%M %p')),
                hangups.ChatMessageSegment('\n', hangups.SegmentType.LINE_BREAK),
                hangups.ChatMessageSegment('Dusk: %s' % sun['dusk'].astimezone(tz).strftime('%I:%M %p'))]

    #output the results
    yield from bot.coro_send_message(event.conv, segments)

