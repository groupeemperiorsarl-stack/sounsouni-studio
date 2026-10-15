import sys,os;sys.argv=['x','none']
exec(open('render.py').read().split("if __name__=='__main__':")[0])
for n,t,dd,li in T:
    if n in('soir','a45','a49','hide','w9','wbgo','peek','run','a50','f43','wserve','w17'): print(n,round(t+min(1.2,dd/2),2))
print(int(TOT*FPS))
