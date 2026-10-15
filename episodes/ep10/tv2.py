import sys;sys.argv=['x','none']
src=open('render_v2.py').read().split("if __name__=='__main__':")[0]
exec(src)
for n,t,dd,li in T:
    if n in('soir','cab','hide','wbgo','w17','fin2'): print(n,repr(t))
print(TOT,FPS)
