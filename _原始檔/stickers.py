"""幹話小人貼紙：IP角色/幹話小人 白底原圖 → 從外框往內 flood fill 去背（小白身體是白的，靠黑色輪廓擋住）→ 白邊 → img/st_*.png
python3 stickers.py"""
import os
import numpy as np, cv2
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = '/Users/ningchang/Library/Mobile Documents/com~apple~CloudDocs/○煦暖曆/03_設計規範/幹話日曆/IP角色/幹話小人'
# 名稱: (原圖, 裁切框 x0,y0,x1,y1 或 None)
ST = {'point': ('ganhua_039_已經長的不好看了，就麻煩你善良一點。.png', None),
      'dance': ('ganhua_003_我的財富自由，就是自由地沒有財富。.png', None),
      'puddle': ('ganhua_019_水不在深，咕嚕咕嚕….。.png', None),
      'lazy': ('ganhua_102_別跟我比懶，我懶得跟你比。.png', (380, 470, 1254, 1254)),
      'phone': ('ganhua_229_人在辦公室，沒在辦公事。.png', None),
      'office': ('ganhua_302_上班不容易，全都靠演技。.png', None),
      'bubble': ('ganhua_050_沒有人可以利用我，因為我根本沒有用。.png', None)}

def cut(path, box, thr=228, stroke=0.012):
    im = np.asarray(Image.open(path).convert('RGB'))
    if box: im = im[box[1]:box[3], box[0]:box[2]]
    h, w = im.shape[:2]; lum = im.mean(axis=2)
    light = (lum > thr).astype(np.uint8)
    pad = np.pad(light, 1, constant_values=1); ff = pad.copy() * 255
    mask = np.zeros((h + 4, w + 4), np.uint8)
    cv2.floodFill(ff, mask, (0, 0), 128)                                      # 從外框連通的淺色＝背景
    bg = ff[1:-1, 1:-1] == 128
    a = (~bg).astype(np.uint8) * 255
    a = cv2.morphologyEx(a, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))       # 去掉零星雜點
    n, lab, stats, _ = cv2.connectedComponentsWithStats(a)
    keep = np.zeros_like(a)
    for i in range(1, n):
        if stats[i, cv2.CC_STAT_AREA] > h * w * 0.0006: keep[lab == i] = 255
    a = keep
    r = max(3, int(max(h, w) * stroke))
    big = cv2.dilate(a, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1)))
    big = cv2.GaussianBlur(big, (0, 0), 1.2)
    out = np.zeros((h, w, 4), np.uint8); out[..., :3] = 255; out[..., 3] = big
    fg = a > 0; out[fg, :3] = im[fg]
    ys, xs = np.nonzero(big > 10); m = r + 4
    y0, y1, x0, x1 = max(0, ys.min() - m), min(h, ys.max() + m), max(0, xs.min() - m), min(w, xs.max() + m)
    return Image.fromarray(out[y0:y1, x0:x1], 'RGBA')

if __name__ == '__main__':
    for k, (f, box) in ST.items():
        s = cut(os.path.join(SRC, f), box); s.thumbnail((520, 520), Image.LANCZOS)
        s.save(os.path.join(HERE, 'img', f'st_{k}.png')); print(k, s.size)
