import sys;sys.argv=['x','none']
exec(open('render.py').read().split("if __name__=='__main__':")[0])
seen=set(); out=[]
for n,t,dd,li in T:
    if n in seen: continue
    seen.add(n); out.append(f"{n}:{t+min(dd*0.6,dd-0.2):.2f}")
print(' '.join(out))
