"""Validate the public image boundary and unchanged original avatar bytes."""
from base64 import b64decode
from pathlib import Path
from unittest import TestCase,main
from unittest.mock import MagicMock,patch
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import profile_avatar


class AvatarDownload(TestCase):
    def test_download_uses_official_host_without_api_credentials(self):
        payload=b'\x89PNG\r\n\x1a\noriginal image bytes'
        response=MagicMock();response.read.return_value=payload
        response.headers.get_content_type.return_value='image/png'
        response.__enter__.return_value=response
        with patch.object(profile_avatar,'urlopen',return_value=response) as download:
            avatar=profile_avatar.fetch('https://avatars.githubusercontent.com/u/123?v=4')
        request=download.call_args.args[0]
        self.assertEqual(request.full_url,'https://avatars.githubusercontent.com/u/123?v=4&s=256')
        self.assertFalse(request.has_header('Authorization'))
        self.assertEqual(b64decode(avatar['data_uri'].split(',')[1]),payload)

    def test_unexpected_host_and_invalid_image_are_rejected(self):
        with patch.object(profile_avatar,'urlopen') as download:
            with self.assertRaises(ValueError):profile_avatar.fetch('https://example.com/avatar.svg')
            download.assert_not_called()
        response=MagicMock();response.read.return_value=b'<svg/>'
        response.headers.get_content_type.return_value='image/svg+xml'
        response.__enter__.return_value=response
        with patch.object(profile_avatar,'urlopen',return_value=response),self.assertRaises(ValueError):
            profile_avatar.fetch('https://avatars.githubusercontent.com/u/123')


if __name__=='__main__':main()
