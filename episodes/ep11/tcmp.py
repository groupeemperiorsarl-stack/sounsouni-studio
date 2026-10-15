import sys,os
src=sys.argv[1]; sys.argv=['x','none']
exec(open(src).read().split("if __name__=='__main__':")[0])
for n,t,dd,li in T:
    if n in('awalk','mef','fin2'): print(n,repr(t),repr(t+dd))
print('TOT',repr(TOT))
