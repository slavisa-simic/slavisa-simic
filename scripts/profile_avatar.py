"""Download the public GitHub avatar and wrap its original pixels in a sharp frame."""
from base64 import b64encode, b64decode
from hashlib import sha256
from html import escape
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode
from urllib.request import Request, urlopen


def fetch(url):
    parts = urlsplit(url)
    if parts.scheme != 'https' or parts.hostname != 'avatars.githubusercontent.com':
        raise ValueError('Expected an official GitHub avatar URL')
    query = dict(parse_qsl(parts.query)); query['s'] = '256'
    url = urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), ''))
    # GitHub credentials are deliberately confined to the API, never the image host.
    request = Request(url, headers={'User-Agent': 'slavisa-profile-avatar', 'Cache-Control': 'no-cache'})
    with urlopen(request, timeout=30) as response:
        payload = response.read(2_000_001)
        mime = response.headers.get_content_type()
    signatures = {'image/png': payload.startswith(b'\x89PNG\r\n\x1a\n'),
                  'image/jpeg': payload.startswith(b'\xff\xd8\xff'),
                  'image/webp': payload.startswith(b'RIFF') and payload[8:12] == b'WEBP'}
    if not payload or len(payload) > 2_000_000 or not signatures.get(mime):
        raise ValueError('Invalid GitHub avatar image')
    return {'source': url, 'mime': mime, 'sha256': sha256(payload).hexdigest(),
            'data_uri': f'data:{mime};base64,' + b64encode(payload).decode('ascii')}


def frame(avatar, palette):
    payload = b64decode(avatar['data_uri'].split(',', 1)[1], validate=True)
    if sha256(payload).hexdigest() != avatar['sha256']:
        raise ValueError('Cached avatar checksum mismatch')
    p = palette
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128" viewBox="0 0 128 128" role="img">'
           '<title>GitHub profile picture</title>'
           '<desc>Current GitHub avatar in a sharp engineering frame. Refreshed automatically every hour.</desc>'
           f'<rect x="1" y="1" width="126" height="126" fill="{p["surface"]}" stroke="{p["line"]}"/>'
           f'<image href="{escape(avatar["data_uri"], quote=True)}" x="12" y="12" width="104" height="104" preserveAspectRatio="xMidYMid meet"/>'
           f'<path d="M1 23V1H23" fill="none" stroke="{p["blue"]}"/>'
           f'<path d="M105 127H127V105" fill="none" stroke="{p["red"]}"/>'
           f'<path d="M119 1H127V9M1 119V127H9" fill="none" stroke="{p["silver"]}"/>'
           '</svg>')
    filename = 'profile-avatar-' + sha256(svg.encode()).hexdigest()[:16] + '.svg'
    return filename, svg
