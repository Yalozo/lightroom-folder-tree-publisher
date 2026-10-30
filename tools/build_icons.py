# Copyright (C) 2026 Yalozo Andrey
# SPDX-License-Identifier: GPL-3.0-only

"""Render the small geometric folder/export mark with no external dependencies."""
from pathlib import Path
import struct
import zlib

ROOT = Path(__file__).resolve().parents[1] / 'FolderTreePublisher.lrplugin'
SHAPES = [
    ('#176c82', [(2,3),(9,3),(11,5),(21,5),(21,16),(2,16)]),
    ('#51c9d5', [(2,6),(21,6),(21,16),(2,16)]),
    ('#ffffff', [(13,10),(17,10),(17,7),(23,12),(17,17),(17,14),(13,14)]),
]

def inside(x,y,points):
    result = False
    for (a,b),(c,d) in zip(points, points[1:]+points[:1]):
        if (b>y) != (d>y) and x < (c-a)*(y-b)/(d-b)+a:
            result = not result
    return result

def render(width,height):
    scale = min(width/24, height/19)
    ox,oy = (width-24*scale)/2,(height-19*scale)/2
    rows=[]
    for y in range(height):
        row=bytearray([0])
        for x in range(width):
            samples=[]
            for sy in range(4):
                for sx in range(4):
                    color=None
                    for hexcolor, points in SHAPES:
                        if inside((x+(sx+.5)/4-ox)/scale,(y+(sy+.5)/4-oy)/scale,points):
                            color=tuple(bytes.fromhex(hexcolor[1:]))
                    if color: samples.append(color)
            n=len(samples)
            row.extend([round(sum(c[i] for c in samples)/n) if n else 0 for i in range(3)]+[round(n/16*255)])
        rows.append(bytes(row))
    def chunk(kind,data):
        return struct.pack('!I',len(data))+kind+data+struct.pack('!I',zlib.crc32(kind+data)&0xffffffff)
    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('!2I5B',width,height,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(b''.join(rows)))+chunk(b'IEND',b'')

for name,w,h in [('icon-small.png',24,19),('icon.png',96,76)]:
    (ROOT/name).write_bytes(render(w,h))
svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 19">\n'
for color,points in SHAPES:
    svg += f'<polygon fill="{color}" points="'+ ' '.join(f'{x},{y}' for x,y in points)+'"/>\n'
(ROOT/'icon.svg').write_text(svg+'</svg>\n')
