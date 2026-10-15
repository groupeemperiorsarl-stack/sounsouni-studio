import sys,os;sys.argv=['x','none']
exec(open('render.py').read().split("if __name__=='__main__':")[0])
for n,t,dd,li in T:
    if n=='w17': print('W17',repr(t))
print('TOT',repr(TOT))
