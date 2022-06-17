from ROOT import TMath

def getBernsteinTerm(n,i,var="x"):
    term = "{0:.0f}*{1}**{2}*(1-{1})**{3:.0f}".format(TMath.Binomial(n,i),var,i,n-i)
    return term

def constructBernstein2D(n,m):
    #Returns two objects
    #1) a string to be used in TFormula constructor defining a 2D Bernstein polynomial of order (n,m) in x and y
    #2) Number of parameters (since this is (n+1)*(m+1), perhaps you can remove this?)
    #The parameters in the string are denoted as @0, @1,...
    TFormulaString = ""
    varCounter = 0

    for i in range(n+1):
        for j in range(m+1):
            termX = getBernsteinTerm(n,i,var="x")            
            termY = getBernsteinTerm(m,j,var="y")
            tempString = "@{0:.0f}*{1}*{2}+".format(varCounter,termX,termY)
            TFormulaString+=tempString
            varCounter+=1
    #TF, nParams
    return TFormulaString[:-1], varCounter+1#removes last "+" in TFormula