#!/usr/bin/env python
# ------------------------------------------------------------------------------------------------------%
# Created by "Chia E Tungom" 12/15/2020                                                                 %
#       Email:      chemago99@yahoo.com                                                                 %
#       Github:     https://github.com/tungom                                                           %
#-------------------------------------------------------------------------------------------------------%

import random
import copy

def RandTravel(costGraph):
    """ Takes a graph and returns
        a random hamiltonian circle route"""
    
    allNodes = [Nodes for Nodes in range(len(costGraph))]
    startNode = random.choice(allNodes)
    TAKEN = [startNode]
    availableNodes = allNodes[:]
    availableNodes.remove(startNode)

    # make sequencial choices 
    while len(availableNodes) > 0:
        nextNode = random.choice(availableNodes)
        TAKEN.append(nextNode)
        startNode = TAKEN[-1]
        availableNodes.remove(nextNode)
    TAKEN.append(TAKEN[0])
    return TAKEN

def TravelCost(CostGraph, route):
    """ takes a costgrpah and a route 
    and returns the cost of the route"""
    return sum([CostGraph[j][route[i+1]] for i,j in enumerate(route) if i < len(route)-1])

def NextNode(Connections, RouletteProb):
    """ Takes nodes and their roulette probabilites and 
    returns one node based on the probability"""
    r = random.random()
    for i in range(len(Connections)):
        if i == 0 and r <= RouletteProb[i]:
            return Connections[i]
        elif r > RouletteProb[i] and r <= RouletteProb[i+1]:
            return Connections[i+1]
        
def Travel(costGraph, pheromoneGraph, alpha = 1, beta = 3, dropout = True):
    """ Takes a cost graph, pheromone graph and returns
        a hamiltonian circle route """
    
    allNodes = [Nodes for Nodes in range(len(costGraph))]
    startNode = random.choice(allNodes)
    TAKEN = [startNode]
    availableNodes = allNodes[:]
    availableNodes.remove(startNode)

    # make sequencial choices 
    while len(availableNodes) > 0:
        
        #--------------- DROP OUT -------------------------------------------------------------------
        usedNodes = availableNodes[:]
        if dropout == True and len(usedNodes) > 1:
            [usedNodes.remove(random.choice(usedNodes)) for i in range(len(usedNodes)) 
             if (random.random() < 0.01 and len(usedNodes)>1)]
        #--------------------------------------------------------------------------------------------
        
        pheromones = [pheromoneGraph[startNode][usedNode] for usedNode in usedNodes]
        costs = [1/costGraph[startNode][usedNode] for usedNode in usedNodes]

        numerators = [(i**alpha)*(j**beta) for i,j in zip(pheromones,costs)]
        probabilities = [i/sum(numerators) for i in numerators]

        RouletteProb = [ sum(probabilities[:i+1]) for i in range(len(probabilities)) ]
        nextNode = NextNode(usedNodes, RouletteProb)
        
        TAKEN.append(nextNode)
        startNode = TAKEN[-1]
        availableNodes.remove(nextNode)
       
    TAKEN.append(TAKEN[0])
    return TAKEN

def Updatepheromone(route, costGraph, pheromoneGraph, rho = 0.5):
    """route : route taken
    pheromoneGraph: pheromone matrix"""
    
    C = TravelCost(costGraph, route)
    tau = 1/C
    #tau = 1
    for i in range(len(route)-1):
        pheromoneGraph[route[i]][route[i+1]] = (1-rho)*(pheromoneGraph[route[i]][route[i+1]]) + tau
        pheromoneGraph[route[i+1]][route[i]] = (1-rho)*(pheromoneGraph[route[i+1]][route[i]]) + tau

    return pheromoneGraph

#------------------------------------ANT SYSTEM--------------------------------------------------------
def AS(costGraph, Population = 8, alpha = 1, beta = 3, rho = 0.5, iterations = 100, dropout = False, show = False):
    """ takes a costgraph, takeoff point, destination point and number of times to travel (iterations)
    and return a tour """
    #-----------------INITIALIZE PHEROMONE----------------------------------------------------------
    RT = RandTravel(costGraph)
    RandCost = TravelCost(costGraph, RT)
    PRM = [[Population/RandCost for i in range(len(costGraph))] for j in range(len(costGraph))]
    
    #-------------------Initialize Ants and Best So Far (BSF) and iteration best IBEST--------------
    Ants = {"Ant" + str(i+1): {"Route": RT, "Cost": RandCost} for i in range(Population)}
    BSF = {"BSF": copy.deepcopy(Ants["Ant1"])}
    IBEST = {"IBEST": copy.deepcopy(Ants["Ant1"])}
    #-----------------------------------------------------------------------------------------------
    while iterations > 0:
        #--------------TRAVEL-----------------------------------------
        for ant in Ants:
            Ants[ant]["Route"] = Travel(costGraph, PRM, alpha, beta, dropout)
            Ants[ant]["Cost"] = TravelCost(costGraph, Ants[ant]["Route"])
            
        #--------------GET ITERATION BEST------------------------------
            if Ants[ant] == Ants["Ant1"]:
                IBEST = {"IBEST": copy.deepcopy(Ants[ant])}
            elif Ants[ant]["Cost"] < IBEST["IBEST"]["Cost"]:
                IBEST = {"IBEST": copy.deepcopy(Ants[ant])}
                
        #-------------GET BEST SO FAR TOUR and UPDATE tmax--------------
        if IBEST["IBEST"]["Cost"] < BSF["BSF"]["Cost"]:
            BSF = {"BSF": copy.deepcopy(IBEST["IBEST"])}
            
        #-------------UPDATE PHEROMONE--------------------------------
        for ant in Ants:
            PRM = Updatepheromone(Ants[ant]["Route"], costGraph, PRM, rho)
        
        #-------------PRINT BSF and IBEST---------------------------------
        if show == True:
            print("Iteration Best is ", IBEST["IBEST"]["Cost"] , " and Best so far is ", BSF["BSF"]["Cost"])
        
        iterations -= 1
        
    return {"Ants": Ants, "PRM":PRM, "BSF":BSF["BSF"]["Cost"], "IBEST":IBEST["IBEST"]["Cost"] }

#----------------------------ELITIST ANT SYSTEM-----------------------------------------------------------

def EASUpdatepheromone(route, BSFR, costGraph, pheromoneGraph, e, rho = 0.1):
    """route : route taken
       BSF : Best sofar route
    pheromoneGraph: pheromone matrix"""
    #--------------------------------GET ARCS--------------------------------------
    BSFarcs = [(j,BSFR[i+1]) for i,j in enumerate(BSFR) if i < len(BSFR)-1]
    routearcs = [(j,route[i+1]) for i,j in enumerate(route) if i < len(route)-1]
    #--------------------COMPUTE COST-----------------------------------------------
    tau = 1/TravelCost(costGraph, route)
    tauBSF = 1/TravelCost(costGraph, BSFR)

    for i,j in routearcs:
        #--------------------CHECK IF ARC IS IN BSF and Update pheromone------------------
        if ((i, j) in BSFarcs) or ((j, i) in BSFarcs):
            pheromoneGraph[i][j] = (1-rho)*(pheromoneGraph[i][j]) + tau + e*tauBSF
            pheromoneGraph[j][i] = (1-rho)*(pheromoneGraph[j][i]) + tau + e*tauBSF
        #----------------------------------------------------------------------------------
        else:
            pheromoneGraph[i][j] = (1-rho)*(pheromoneGraph[i][j]) + tau 
            pheromoneGraph[j][i] = (1-rho)*(pheromoneGraph[j][i]) + tau 

    return pheromoneGraph

def EAS(costGraph, Population = 8, alpha = 1, beta = 3, rho = 0.5, iterations = 100, dropout = False, show = False):
    
    """ takes a costgraph, takeoff point, destination point and number of times to travel (iterations)
    and return a tour """
    
    e = len(costGraph)
    #-----------------INITIALIZE PHEROMONE----------------------------------------------------------
    
    RT = RandTravel(costGraph)
    RandCost = TravelCost(costGraph, RT)
    PRM = [[Population/RandCost for i in range(len(costGraph))] for j in range(len(costGraph))]
    
    #-------------------Initialize Ants and Best So Far (BSF) and iteration best IBEST--------------
    Ants = {"Ant" + str(i+1): {"Route": RT, "Cost": RandCost} for i in range(Population)}
    BSF = {"BSF": copy.deepcopy(Ants["Ant1"])}
    IBEST = {"IBEST": copy.deepcopy(Ants["Ant1"])}
    #-----------------------------------------------------------------------------------------------
    while iterations > 0:
        #--------------TRAVEL-----------------------------------------
        for ant in Ants:
            Ants[ant]["Route"] = Travel(costGraph, PRM, alpha, beta)
            Ants[ant]["Cost"] = TravelCost(costGraph, Ants[ant]["Route"])
            
        #--------------GET ITERATION BEST------------------------------
            if Ants[ant] == Ants["Ant1"]:
                IBEST = {"IBEST": copy.deepcopy(Ants[ant])}
            elif Ants[ant]["Cost"] < IBEST["IBEST"]["Cost"]:
                IBEST = {"IBEST": copy.deepcopy(Ants[ant])}
                
        #-------------GET BEST SO FAR TOUR and UPDATE tmax--------------
        if IBEST["IBEST"]["Cost"] < BSF["BSF"]["Cost"]:
            BSF = {"BSF": copy.deepcopy(IBEST["IBEST"])}
            
        #-------------UPDATE PHEROMONE--------------------------------
        for ant in Ants:
            PRM = EASUpdatepheromone(Ants[ant]["Route"], BSF["BSF"]["Route"], costGraph, PRM, e, rho)
            
        #-------------PRINT BSF and IBEST---------------------------------
        if show == True:
            print("Iteration Best is ", IBEST["IBEST"]["Cost"] , " and Best so far is ", BSF["BSF"]["Cost"])
        
        iterations -= 1
        
    return {"Ants": Ants, "PRM":PRM, "BSF":BSF["BSF"]["Cost"], "IBEST":IBEST["IBEST"]["Cost"] }

#-------------------------------RANKED_BASED ANT SYSTEM----------------------------------------------------

def RBASUpdatepheromone(route, BSFR, costGraph, pheromoneGraph, rank, w, rho = 0.1):
    """route : route taken
       BSF : Best sofar route
    pheromoneGraph: pheromone matrix"""
    #--------------------------------GET ARCS--------------------------------------
    BSFarcs = [(j,BSFR[i+1]) for i,j in enumerate(BSFR) if i < len(BSFR)-1]
    routearcs = [(j,route[i+1]) for i,j in enumerate(route) if i < len(route)-1]
    #--------------------COMPUTE COST-----------------------------------------------
    tau = 1/TravelCost(costGraph, route)
    tauBSF = 1/TravelCost(costGraph, BSFR)

    for i,j in routearcs:
        #--------------------CHECK IF ARC IS IN BSF and Update pheromone------------------
        if ((i, j) in BSFarcs) or ((j, i) in BSFarcs):
            pheromoneGraph[i][j] = (1-rho)*(pheromoneGraph[i][j]) + (w-rank)*tau + w*tauBSF
            pheromoneGraph[j][i] = (1-rho)*(pheromoneGraph[j][i]) + (w-rank)*tau + w*tauBSF
        #----------------------------------------------------------------------------------
        else:
            pheromoneGraph[i][j] = (1-rho)*(pheromoneGraph[i][j]) + (w-rank)*tau 
            pheromoneGraph[j][i] = (1-rho)*(pheromoneGraph[j][i]) + (w-rank)*tau 

    return pheromoneGraph

def RBAS(costGraph, Population = 8, alpha = 1, beta = 3, rho = 0.1, iterations = 100, dropout = False, show = False):
    
    """ takes a costgraph, takeoff point, destination point and number of times to travel (iterations)
    and return a tour """
    w = 6
    #-----------------INITIALIZE PHEROMONE----------------------------------------------------------
    RT = RandTravel(costGraph)
    RandCost = TravelCost(costGraph, RandTravel(costGraph))
    PRM = [[Population/RandCost for i in range(len(costGraph))] for j in range(len(costGraph))]
    
    #-------------------Initialize Ants and Best So Far (BSF) and iteration best IBEST--------------
    Ants = {"Ant" + str(i+1): {"Route": RT, "Cost": RandCost} for i in range(Population)}
    BSF = {"BSF": copy.deepcopy(Ants["Ant1"])}
    IBEST = {"IBEST": copy.deepcopy(Ants["Ant1"])}
    #-----------------------------------------------------------------------------------------------
    while iterations > 0:
        #--------------TRAVEL-----------------------------------------
        for ant in Ants:
            Ants[ant]["Route"] = Travel(costGraph, PRM, alpha, beta)
            Ants[ant]["Cost"] = TravelCost(costGraph, Ants[ant]["Route"])
            
        #--------------GET ITERATION BEST------------------------------
            if Ants[ant] == Ants["Ant1"]:
                IBEST = {"IBEST": copy.deepcopy(Ants[ant])}
            elif Ants[ant]["Cost"] < IBEST["IBEST"]["Cost"]:
                IBEST = {"IBEST": copy.deepcopy(Ants[ant])}
                
        #-------------GET BEST SO FAR TOUR and UPDATE tmax--------------
        if IBEST["IBEST"]["Cost"] < BSF["BSF"]["Cost"]:
            BSF = {"BSF": copy.deepcopy(IBEST["IBEST"])}
            
        #---------------RANK ANTS---------------------------------------      
        Ranks = sorted([(Ants[ant]["Cost"], ant) for ant in Ants]) 
        for i,j in enumerate(Ranks):
            Ants[j[1]]["Rank"] = i+1
            
        #-------------UPDATE PHEROMONE--------------------------------
        for ant in Ants:
            r = Ants[ant]["Rank"]
            if r < w:
                PRM = RBASUpdatepheromone(Ants[ant]["Route"], BSF["BSF"]["Route"], costGraph, PRM, r, w, rho)
                
        #-------------PRINT BSF and IBEST---------------------------------
        if show == True:
            print("Iteration Best is ", IBEST["IBEST"]["Cost"] , " and Best so far is ", BSF["BSF"]["Cost"])
        
        iterations -= 1
        
    return {"Ants": Ants, "PRM":PRM, "BSF":BSF["BSF"]["Cost"], "IBEST":IBEST["IBEST"]["Cost"] }

#----------------------------ANT COLONY SYSTEM-------------------------------------------------------------------

def PseudoNextNode(Connections, Pseudovalues):
    return Connections[Pseudovalues.index(max(Pseudovalues))]

def ACSTravel(costGraph, pheromoneGraph, t0, eps = 0.1, q0 = 0.9, alpha=1, beta=2 , dropout = False):
    """ Takes a cost graph, pheromone graph and returns
        a hamiltonian circle route """
    
    allNodes = [Nodes for Nodes in range(len(costGraph))]
    startNode = random.choice(allNodes)
    TAKEN = [startNode]
    availableNodes = allNodes[:]
    availableNodes.remove(startNode)

    # make sequencial choices 
    while len(availableNodes) > 0:
        
        #--------------- DROP OUT -------------------------------------------------------------------
        usedNodes = availableNodes[:]
        if dropout == True and len(usedNodes) > 1:
            [usedNodes.remove(random.choice(usedNodes)) for i in range(len(usedNodes)) 
             if (random.random()<0.005 and len(usedNodes)>1)]
        #--------------------------------------------------------------------------------------------
        
        pheromones = [pheromoneGraph[startNode][availableNode] for availableNode in usedNodes]
        costs = [1/costGraph[startNode][availableNode] for availableNode in usedNodes]
        #------------------CHOOSE NODE--------------------------------------------------------------   
        if random.random() < q0:
            Pseudovalues = [(i)*(j**beta) for i,j in zip(pheromones,costs)]
            nextNode = PseudoNextNode(usedNodes, Pseudovalues)
        else:
            numerators = [(i**alpha)*(j**beta) for i,j in zip(pheromones,costs)]
            probabilities = [i/sum(numerators) for i in numerators]
            RouletteProb = [ sum(probabilities[:i+1]) for i in range(len(probabilities)) ]
            nextNode = NextNode(usedNodes, RouletteProb)
        #----------------LOCAL PHEROMONE UPDATE-----------------------------------------------------
        pheromoneGraph = ACSUpdatepheromoneLocal(pheromoneGraph, startNode, nextNode, t0, eps)
        
        TAKEN.append(nextNode)
        startNode = TAKEN[-1]
        availableNodes.remove(nextNode)
        
    TAKEN.append(TAKEN[0])
    return TAKEN

def ACSUpdatepheromone(route, costGraph, pheromoneGraph, rho = 0.1):
    """route : route taken
       BSF : Best sofar route
    pheromoneGraph: pheromone matrix"""
    #--------------------------------GET ARCS--------------------------------------
    routearcs = [(j,route[i+1]) for i,j in enumerate(route) if i < len(route)-1]
    #--------------------COMPUTE COST-----------------------------------------------
    tau = 1/TravelCost(costGraph, route)
    
    for i,j in routearcs:
        pheromoneGraph[i][j] = (1-rho)*(pheromoneGraph[i][j]) + rho*tau
        pheromoneGraph[j][i] = (1-rho)*(pheromoneGraph[i][j]) + rho*tau
    return pheromoneGraph

def ACSUpdatepheromoneLocal(pheromoneGraph, start, end, t0, eps = 0.1):
    pheromoneGraph[start][end] = (1-eps)*pheromoneGraph[start][end] + eps*t0
    pheromoneGraph[end][start] = (1-eps)*pheromoneGraph[end][start] + eps*t0
    return pheromoneGraph

def ACS(costGraph, Population = 10, eps = 0.1, q0 = 0.9, alpha = 1, beta = 3, rho = 0.1, iterations = 100, dropout = False, show = False):
    
    """ takes a costgraph, takeoff point, destination point and number of times to travel (iterations)
    and return a tour """
    
    #-----------------INITIALIZE PHEROMONE and SET UPPER and LOWER Limit-----------------------
    RT = RandTravel(costGraph)
    RandCost = TravelCost(costGraph, RT)
    t0 = 1/( (len(costGraph))*RandCost )
                
    PRM = [[t0 for i in range(len(costGraph))] for j in range(len(costGraph))]
    
    #-------------------Initialize Ants and Best So Far (BSF) and iteration best IBEST--------------
    Ants = {"Ant" + str(i+1): {"Route": RT, "Cost": RandCost} for i in range(Population)}
    BSF = {"BSF": copy.deepcopy(Ants["Ant1"])}
    IBEST = {"IBEST": copy.deepcopy(Ants["Ant1"])}
    #-----------------------------------------------------------------------------------------------
    while iterations > 0:
        #--------------TRAVEL-----------------------------------------
        for ant in Ants:
            Ants[ant]["Route"] = ACSTravel(costGraph, PRM, t0, eps , q0 , alpha, beta, dropout)
            Ants[ant]["Cost"] = TravelCost(costGraph, Ants[ant]["Route"])
            
        #--------------GET ITERATION BEST------------------------------
            if Ants[ant] == Ants["Ant1"]:
                IBEST = {"IBEST": copy.deepcopy(Ants[ant])}
            elif Ants[ant]["Cost"] < IBEST["IBEST"]["Cost"]:
                IBEST = {"IBEST": copy.deepcopy(Ants[ant])}
                
        #-------------GET BEST SO FAR TOUR and UPDATE tmax--------------
        if IBEST["IBEST"]["Cost"] < BSF["BSF"]["Cost"]:
            BSF = {"BSF": copy.deepcopy(IBEST["IBEST"])}
            
        #-------------UPDATE PHEROMONE BY IBEST or BSF------------------
        ACSUpdatepheromone(BSF["BSF"]["Route"], costGraph, PRM, rho)
        #ACSUpdatepheromone(IBEST["IBEST"]["Route"], costGraph, PRM, rho)
        
        #-------------PRINT BSF and IBEST---------------------------------
        if show == True:
            print("Iteration Best is ", IBEST["IBEST"]["Cost"] , " and Best so far is ", BSF["BSF"]["Cost"])
        
        iterations -= 1
        
    return {"Ants": Ants, "PRM":PRM, "BSF":BSF["BSF"]["Cost"], "IBEST":IBEST["IBEST"]["Cost"] }

#---------------------------------MIN MAX ANT SYSTEM--------------------------------------------------------

def MMASUpdatepheromone(route, costGraph, pheromoneGraph, tmax):
    """route : route taken
       BSF : Best sofar route
    pheromoneGraph: pheromone matrix"""
    #--------------------------------GET ARCS--------------------------------------
    routearcs = [(j,route[i+1]) for i,j in enumerate(route) if i < len(route)-1]
    #--------------------COMPUTE COST-----------------------------------------------
    tau = 1/TravelCost(costGraph, route)

    for i,j in routearcs:
        pheromoneGraph[i][j] += tau
        if pheromoneGraph[i][j] > tmax:
            pheromoneGraph[i][j] = tmax
            pheromoneGraph[j][i] = tmax
        else:
            pheromoneGraph[j][i] += tau
    return pheromoneGraph

def MMASevaporate(route, pheromoneGraph, tmin, rho = 0.02):
    #------------------------------------------------------------------------------
    routearcs = [(j,route[i+1]) for i,j in enumerate(route) if i < len(route)-1]    
    #--------------------COMPUTE COST----------------------------------------------
    for i,j in routearcs:
        pheromoneGraph[i][j] = (1-rho)*(pheromoneGraph[i][j])
        if pheromoneGraph[i][j] < tmin:
            pheromoneGraph[i][j] = tmin
            pheromoneGraph[j][i] = tmin
        else:
            pheromoneGraph[j][i] = (1-rho)*(pheromoneGraph[j][i])
    return pheromoneGraph

def MMAS(costGraph, Population = 8, alpha = 1, beta = 3, rho = 0.02, iterations = 100, dropout = False, show = False):
    
    """ takes a costgraph, takeoff point, destination point and number of times to travel (iterations)
    and return a tour """
    t = 0   # stagnation measure
    #-----------------INITIALIZE PHEROMONE and SET UPPER and LOWER Limit-----------------------
    RT = RandTravel(costGraph)
    RandCost = TravelCost(costGraph, RT)
    tmax = 1/(rho*RandCost)
    num = tmax*(1- (0.05**(1/Population)))
    den = ((len(costGraph)/2) - 1 )*(0.05**(1/Population))          
    tmin = num/den
                
    PRM = [[tmax for i in range(len(costGraph))] for j in range(len(costGraph))]
    
        #-------------------Initialize Ants and Best So Far (BSF) and iteration best IBEST--------------
    Ants = {"Ant" + str(i+1): {"Route": RT, "Cost": RandCost} for i in range(Population)}
    BSF = {"BSF": copy.deepcopy(Ants["Ant1"])}
    IBEST = {"IBEST": copy.deepcopy(Ants["Ant1"])}
    #-----------------------------------------------------------------------------------------------
    while iterations > 0:
        #--------------TRAVEL-----------------------------------------
        for ant in Ants:
            Ants[ant]["Route"] = Travel(costGraph, PRM, alpha, beta, dropout)
            Ants[ant]["Cost"] = TravelCost(costGraph, Ants[ant]["Route"])
            
        #--------------GET ITERATION BEST------------------------------
            if Ants[ant] == Ants["Ant1"]:
                IBEST = {"IBEST": copy.deepcopy(Ants[ant])}
            elif Ants[ant]["Cost"] < IBEST["IBEST"]["Cost"]:
                IBEST = {"IBEST": copy.deepcopy(Ants[ant])}
                
        #-------------GET BEST SO FAR TOUR and UPDATE tmax--------------
        if IBEST["IBEST"]["Cost"] < BSF["BSF"]["Cost"]:
            BSF = {"BSF": copy.deepcopy(IBEST["IBEST"])}
            
            tmax = 1/(rho*BSF["BSF"]["Cost"])
            num = tmax*(1- (0.05**(1/Population)))
            tmin = num/den
            t = 0
        else:
            t += 1

        #---------------OCCASIONAL PHEROMONE REINITIALIZATION-----------
        if t >= random.uniform(15,30):
            # print("REINITALIZATION INITIATED ")
            PRM = [[tmax for i in range(len(costGraph))] for j in range(len(costGraph))]
            t = 0
        #---------------EVAPORATE PHEROMONE FROM ALL ANTS---------------      
        for ant in Ants:
            PRM = MMASevaporate(Ants[ant]["Route"], PRM, tmin, rho) 
            
        #-------------UPDATE PHEROMONE BY IBEST or BSF------------------
        
        if random.random()<0.5:
            PRM = MMASUpdatepheromone(IBEST["IBEST"]["Route"], costGraph, PRM, tmax)
        else:
            PRM = MMASUpdatepheromone(BSF["BSF"]["Route"], costGraph, PRM, tmax)
       
        #-------------PRINT BSF and IBEST---------------------------------
        if show == True:
            print("Iteration Best is ", IBEST["IBEST"]["Cost"] , " and Best so far is ", BSF["BSF"]["Cost"])
        
        iterations -= 1
        
    return {"Ants": Ants, "PRM":PRM, "BSF":BSF["BSF"]["Cost"], "IBEST":IBEST["IBEST"]["Cost"] }