class Error(Exception):
    def __init__(self,*a,**k): super().__init__(*a)
def Info(*a,**k): pass
def Warning(*a,**k): pass
