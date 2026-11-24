"""手機版幹話曆落地頁 v1（2026-11-25）：產生頁面用的靜態素材 → img/
- Widget：幹話曆手機版內頁（印刷檔重排，1/1–2/13 共 44 天，make_screen.card_from_phone），830×863 圓角
- 不用的句子：1/6（屎）、2/4（禽獸）、1/12（死亡梗）、1/23（埋了別人）、1/20（沒用的你）
  例外：三種尺寸／長按換尺寸用 App 真實截圖（小中大都是 JAN. 22，內容是印刷 1/20 那句），沿用尺寸切換影片
- 受眾卡照片：幹話曆手機版情境圖綠幕原圖重新合成，手機裡跟放大卡同一天；星期對場景（通勤、上班用平日，咖啡廳用週六）
- 交換禮物卡：旅行曆綠幕「飯店房間地圖」（朋友在國外）換成幹話曆 1/25
python3 -E -P assets.py"""
import os, sys, datetime
from functools import lru_cache
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = '/Users/ningchang/Library/Mobile Documents/com~apple~CloudDocs/○煦暖曆'
IMG = os.path.join(HERE, 'img'); os.makedirs(IMG, exist_ok=True)
sys.path.insert(0, os.path.join(ROOT, '01_廣告投放/手機版日曆/成片/小編開箱/工作檔'))
import storyboard as SB
P, MA, TR = SB.P, SB.MA, SB.TR
sys.path.insert(0, os.path.join(ROOT, '01_廣告投放/幹話日曆/情境圖/手機版情境圖/工作檔'))
import make_screen as MS
KIND = '幹話曆'
AVOID = {'1/6', '2/4', '1/12', '1/23', '1/20'}
APP_DAY = '1/22'                     # App 尺寸截圖上寫的日期

WK = '一二三四五六日'
_ORIG_ICON = P.icon.__wrapped__

def mmdd(md): mo, da = map(int, md.split('/')); return f'{mo:02d}-{da:02d}'

def set_day(md):
    """主畫面「行事曆」圖示換成那一天（原本固定寫週五 22）"""
    mo, da = map(int, md.split('/')); wk = '週' + WK[datetime.date(2027, mo, da).weekday()]
    @lru_cache(None)
    def icon(name):
        if name != 'Calendar': return _ORIG_ICON(name)
        s = int(P.ICON * P.PT)
        im = Image.new('RGBA', (s, s), (255, 255, 255, 255)); d = ImageDraw.Draw(im)
        d.text((s / 2, s * 0.24), wk, font=P.font(10.5, 'Medium'), fill=(232, 58, 48), anchor='mm')
        d.text((s / 2, s * 0.62), str(da), font=P.sf(33, 'Light'), fill=(20, 20, 22), anchor='mm')
        m = P.rmask(s, s, int(s * 0.225)); out = Image.new('RGBA', (s, s), (0, 0, 0, 0)); out.paste(im, (0, 0), m)
        return out
    P.icon = icon; P.app_sprite.cache_clear(); P.static_bg.cache_clear()

@lru_cache(None)
def widget(md):
    """830×863 圓角透明的 Widget（RGBA）"""
    assert md not in AVOID, md
    c = MS.card_from_phone(mmdd(md)).convert('RGBA')
    c.putalpha(MS.rounded_mask(c.width, c.height, round(c.width * 0.085))); return c

def save_widget(md, px, name, folder=IMG):
    w = widget(md); w.resize((px, round(px * w.height / w.width)), Image.LANCZOS).save(os.path.join(folder, name))

def screen(md, size='L'):
    """md=None：用 App 截圖（日期 1/22）"""
    if md is None or size != 'L':
        set_day(APP_DAY); src = P.WIDGETS[KIND][size][0]
    else:
        assert md not in AVOID, md
        set_day(md); src = f'g:{mmdd(md)}'
    return SB.screen(KIND, size, src)

def compose_still(path, md, box, out_wh):
    im = cv2.cvtColor(cv2.imread(path), cv2.COLOR_BGR2RGB); Q, _ = TR.quad_of(im)
    ow, oh = MA.OW, MA.OH; MA.OW, MA.OH = out_wh
    try: a = MA.compose(im, np.array(Q, float), screen(md), np.random.default_rng(1), box)
    finally: MA.OW, MA.OH = ow, oh
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))

def green_info(path):
    im = cv2.imread(path); a = im.astype(int)
    g = (a[..., 1] - np.maximum(a[..., 0], a[..., 2])) > 60; ys, xs = np.nonzero(g)
    return im.shape[1], im.shape[0], (xs.min(), ys.min(), xs.max(), ys.max())

G_GH = os.path.join(ROOT, '01_廣告投放/幹話日曆/情境圖/手機版情境圖/工作檔/綠幕原圖')
G_XW = os.path.join(ROOT, '99_系統工具/產品廣告圖工具/手機版情境圖/綠幕原圖')
CARDS = [('p1', os.path.join(G_GH, 'S4_咖啡廳_01-09.jpg'), '1/2'),        # 週六咖啡廳：我是一個很自律的人，每次下定決心都撐不過第二天
         ('p2', os.path.join(G_GH, 'S2_辦公桌_01-27.jpg'), '1/4'),        # 週一辦公桌：我上班領的不是薪水，是精神賠償金
         ('p3', os.path.join(G_XW, '08_旅行曆_S3_飯店房間地圖.jpg'), '1/25'),  # 朋友在國外：世界上最甜的蜜不是蜂蜜，是 you and me
         ('p4', os.path.join(G_GH, 'S1_通勤_01-04.jpg'), '1/27')]          # 週三通勤：今日事今日畢，做不到就放棄
PIC_W, PIC_H = 960, 1000

def cards():
    for name, path, md in CARDS:
        W, H, (gx0, gy0, gx1, gy1) = green_info(path)
        ch = min(H, W * PIC_H / PIC_W); cw = ch * PIC_W / PIC_H
        ph = gy1 - gy0
        if ch > ph * 2.6: ch = ph * 2.6; cw = ch * PIC_W / PIC_H
        cx = (gx0 + gx1) / 2; cy = (gy0 + gy1) / 2 - ch * 0.04
        x0 = float(np.clip(cx - cw / 2, 0, W - cw)); y0 = float(np.clip(cy - ch / 2 + ch * 0.06, 0, H - ch))
        compose_still(path, md, (x0, y0, cw, ch), (PIC_W, PIC_H)).save(os.path.join(IMG, f'{name}.jpg'), quality=90)
        save_widget(md, 330, f'{name}_w.png')
        print(name, md, (round(x0), round(y0), round(cw), round(ch)), flush=True)

WALL = ['1/1', '1/2', '1/3', '1/4', '1/5', '1/7', '1/8', '1/9', '1/10', '1/11', '1/13', '1/14',
        '1/15', '1/16', '1/17', '1/18', '1/19', '1/21', '1/22', '1/24', '1/25', '1/26', '1/27', '1/28']
DAYS6 = ['1/1', '1/3', '1/8', '1/13', '1/24', '1/31']

def wall():
    os.makedirs(os.path.join(IMG, 'wall'), exist_ok=True)
    for i, md in enumerate(WALL): save_widget(md, 230, f'{i + 1:02d}.png', os.path.join(IMG, 'wall'))
    print('wall', len(WALL), flush=True)

def anatomy():
    for md in DAYS6: save_widget(md, 620, f'a_{md.replace("/", "-")}.png')
    print('anatomy', flush=True)

def lock():
    """收尾鎖定畫面：桌布用幹話曆手機桌面的深藍桌布，Widget 1/1"""
    bg = P.wallpaper(KIND).convert('RGB')
    s = max(960 / bg.width, 1500 / bg.height); bg = bg.resize((round(bg.width * s), round(bg.height * s)), Image.LANCZOS)
    x = (bg.width - 960) // 2; y = (bg.height - 1500) // 2
    bg.crop((x, y, x + 960, y + 1500)).filter(ImageFilter.GaussianBlur(6)).save(os.path.join(IMG, 'lock_bg.jpg'), quality=88)
    save_widget('1/1', 620, 'lock_w.png')

def sizes():
    for sz in ['S', 'M', 'L']:
        s = screen(None, sz)
        Image.fromarray(np.clip(s, 0, 255).astype(np.uint8)).resize((330, round(330 * s.shape[0] / s.shape[1])), Image.LANCZOS).save(os.path.join(IMG, f'scr_{sz}.png'))
    print('sizes', flush=True)

if __name__ == '__main__':
    sel = sys.argv[1:] or ['cards', 'wall', 'anatomy', 'lock', 'sizes']
    for s in sel: globals()[s]()
