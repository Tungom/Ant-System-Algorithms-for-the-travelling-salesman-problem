# A random graph
import random 

def RandGraph(dim = 10, domain = (2,4)):
    """ dim: size of a the graph
        domain: domain of cost 
        retuns a symmetric matrix"""
    
    b = [(i, str(i)) for i in range(dim)]   
    matrix = []
    for i,j in b:
        j=[]
        if i == 0:
            j.append(0)
            matrix.append(j)
        else:
            for k in range(i+1):
                if k == i:
                    j.append(0)
                else:
                    j.append(random.uniform(domain[0],domain[1]))
            matrix.append(j)      
    M = matrix        
    for i in range(len(M)):
        for j in range(1,len(M)-len(M[i])+1):
            M[i].append(M[i+j][i])    
    return M