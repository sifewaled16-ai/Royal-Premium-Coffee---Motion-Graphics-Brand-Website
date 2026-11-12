from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math, os, subprocess, wave, struct
W,H,FPS,SECONDS=720,1280,30,15
os.makedirs("out",exist_ok=True)
def font(size,bold=False):
    paths=["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
    for p in paths:
        if os.path.exists(p): return ImageFont.truetype(p,size)
    return ImageFont.load_default()
gold=(224,181,103); cream=(248,235,211); red=(157,20,28)
def frame(t):
    im=Image.new("RGB",(W,H),(10,7,6))
    glow=Image.new("RGBA",(W,H),(0,0,0,0)); gd=ImageDraw.Draw(glow)
    for r in range(380,20,-12):
        a=int(3+(380-r)*.07)
        gd.ellipse((W//2-r,390-r,W//2+r,390+r),fill=(150,65,22,a))
    im=Image.alpha_composite(im.convert("RGBA"),glow.filter(ImageFilter.GaussianBlur(50)))
    d=ImageDraw.Draw(im)
    # moving gold streaks
    for i in range(7):
        y=int((t*170+i*215)%H)
        d.line((0,y,W,y-80),fill=(110,77,35,55),width=2)
    # orbit
    cx,cy=W//2,550
    d.ellipse((cx-210,cy-210,cx+210,cy+210),outline=(190,145,75,110),width=2)
    d.ellipse((cx-178,cy-178,cx+178,cy+178),outline=(190,145,75,55),width=1)
    # animated premium pouch silhouette
    bob=math.sin(t*2.5)*14
    x,y=cx-112,int(280+bob)
    pouch=Image.new("RGBA",(W,H),(0,0,0,0)); p=ImageDraw.Draw(pouch)
    p.polygon([(x+10,y),(x+214,y),(x+207,y+460),(x+112,y+485),(x+17,y+460)],fill=(145,15,25,255),outline=gold,width=4)
    p.line((x+12,y+30,x+212,y+30),fill=(245,205,140,190),width=4)
    p.ellipse((cx-57,y+100,cx+57,y+214),outline=gold,width=3)
    p.text((cx,y+153),"♛",font=font(72,True),fill=gold,anchor="mm")
    p.text((cx,y+258),"ROYAL",font=font(29,True),fill=cream,anchor="mm")
    p.text((cx,y+300),"PREMIUM",font=font(25,True),fill=gold,anchor="mm")
    p.text((cx,y+337),"COFFEE",font=font(29,True),fill=cream,anchor="mm")
    p.line((x+48,y+380,x+166,y+380),fill=gold,width=2)
    p.text((cx,y+414),"125 g  •  FRESH ROAST",font=font(13,True),fill=cream,anchor="mm")
    im=Image.alpha_composite(im,pouch)
    d=ImageDraw.Draw(im)
    # typography scene changes
    scenes=[
      (0,3.0,"A ROYAL COFFEE","EXPERIENCE"),
      (3.0,6.0,"BOLD AROMA.","RICH CHARACTER."),
      (6.0,9.0,"بن ملوكي فاخر","قهوة بمذاق ملكي"),
      (9.0,12.0,"MADE FOR","YOUR MOMENT"),
      (12.0,15.0,"ROYAL PREMIUM","COFFEE")
    ]
    for a,b,l1,l2 in scenes:
      if a<=t<b:
        alpha=int(255*min(1,(t-a)/.35,(b-t)/.3))
        d.text((W//2,890),l1,font=font(36 if len(l1)<20 else 31,True),fill=(*gold,alpha),anchor="mm",stroke_width=1,stroke_fill=(30,18,8,alpha))
        d.text((W//2,948),l2,font=font(25,True),fill=(*cream,alpha),anchor="mm")
        break
    # progress line and footer
    d.rectangle((65,1110,655,1113),fill=(90,68,39,255))
    d.rectangle((65,1110,65+int(590*t/SECONDS),1113),fill=gold)
    d.text((W//2,1160),"PREMIUM MOTION DESIGN  •  ROASTED WITH CARE",font=font(13,True),fill=(190,160,112),anchor="mm")
    return im.convert("RGB")
raw="out/frames.mp4"
cmd=["ffmpeg","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-an","-c:v","libx264","-preset","ultrafast","-pix_fmt","yuv420p",raw]
proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
for i in range(FPS*SECONDS):
    proc.stdin.write(frame(i/FPS).tobytes())
proc.stdin.close()
if proc.wait()!=0: raise SystemExit("video render failed")
# Original subtle cinematic sound bed: soft low pulse + bright accents, no copyrighted music
import numpy as np
sr=44100; n=sr*SECONDS
t=np.arange(n)/sr
audio=.055*np.sin(2*np.pi*55*t)+.025*np.sin(2*np.pi*110*t)
for sec in [0.25,3.0,6.0,9.0,12.0]:
    start=int(sec*sr); dur=min(int(.55*sr),n-start)
    env=np.exp(-np.arange(dur)/(sr*.13))
    audio[start:start+dur]+=.16*env*np.sin(2*np.pi*(660+sec*13)*np.arange(dur)/sr)
audio=np.clip(audio,-.8,.8)
with wave.open("out/bed.wav","wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
    w.writeframes((audio*32767).astype("<i2").tobytes())
subprocess.run(["ffmpeg","-y","-i",raw,"-i","out/bed.wav","-c:v","copy","-c:a","aac","-b:a","128k","-shortest","out/royal-premium-motion.mp4"],check=True)
