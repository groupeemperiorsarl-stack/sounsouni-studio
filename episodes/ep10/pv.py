import sys; sys.argv=['x','none']
exec(open('render.py').read().split("if __name__=='__main__':")[0])
from PIL import Image
want=sys_want=['w9','w10','wbgo','wgive','wserve','w17']
ts=[(n,round(t0+dd*0.6,2)) for n,t0,dd,li in T if n in want]
S=Image.new('RGB',(10*130,2*231))
for i,(n,t) in enumerate(ts):
    try: f=frame_at(t)
    except Exception as e: print('ERR',n,repr(e)[:160]); continue
    S.paste(f.resize((130,231)),((i%10)*130,(i//10)*231))
S.save('pv.png'); print('ok')
