"""Encode deterministic six-second GIF loops with a shared palette and delta frames."""
from PIL import Image, ImageChops
from profile_common import ROOT, MEDIA


def main():
    for variant in ('activity-commits', 'activity-commits-mobile'):
        paths = [ROOT/'assets/profile/build'/variant/f'{i:03}.png' for i in range(48)]
        frames = []
        for path in paths:
            with Image.open(path) as image:
                frames.append(image.convert('RGB'))
        width, height = frames[0].size
        sample = Image.new('RGB', (width*3, height))
        for i,index in enumerate((0,16,32)):
            sample.paste(frames[index], (i*width,0))
        palette = sample.quantize(colors=128)
        indexed = [frame.quantize(palette=palette,dither=Image.Dither.NONE) for frame in frames]
        target = MEDIA/(variant+'.gif')
        temporary = target.with_suffix('.tmp')
        indexed[0].save(temporary,format='GIF',save_all=True,append_images=indexed[1:],
                        duration=[120,130]*24,loop=0,optimize=True,disposal=1)
        with Image.open(temporary) as result:
            assert result.n_frames == 48 and result.info['loop'] == 0
            first = result.convert('RGB')
            result.seek(24)
            assert ImageChops.difference(first,result.convert('RGB')).getbbox(), 'Animation has no visible motion'
            assert temporary.stat().st_size < 2_000_000, 'Activity GIF exceeds 2 MB budget'
        temporary.replace(target)
        print(f'{variant}: {target.stat().st_size:,} bytes, 48 frames')


if __name__ == '__main__':
    main()
