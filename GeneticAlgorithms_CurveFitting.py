#This returns a number N in the inclusive range [a,b], meaning a <= N <= b, where the endpoints are included in the range.
#print(random.random())
#Random floating point values can be generated using the random() function. Values will be generated in the range between 0 and 1, specifically in the interval [0,1).
#print(random.randint(0,9))
#The random.uniform() function returns a random floating-point number between a given range in Python. 
#print(random.uniform(0.1,0.2))

import random

#To write console Output in a text file and save it in a given path
import sys
import math

#Probability of crossover and mutation
PC = 0.7
PM = 0.1
minRange = -10
maxRange =  10
dependencyFactor = 2

#Step 1: Initilaize Population
#We can represent a solution (the items selected) as a chromosome containing N bits where N is number of degree of curve 
#plus one each bit (i) corresponds to a random float point value (i) in range given [-10,10]
#These functions return arrays containing arrays of representing population and  individuals
#Since we want to find the best coefficients that minimize the error, our chromosome will
#be represented in floating point and its size will be D+1 where each bit represents a 
#coefficient in the equation
def InitializeIndividual(size):
    
    individual=[]

    for i in range(size):
        individual.append(round(random.uniform(minRange,maxRange),1))

    return individual

def InitializePopulation(populationSize,individualSize):

    population=[]

    for i in range(populationSize):
        population.append(InitializeIndividual(individualSize))

    return population

#Step 2: Let’s evaluate the fitness of each chromosome using the objective function 
#Then, we can use the mean square error as our fitness function
#Let’s evaluate the fitness of each chromosome. We will need to use the root mean 
#square error sqrt(1/N ∑N (ycalc. – yactual)^2) between every given point and the polynomial.
#This function returns an array of fitness values corresponding each population in array returned by InitializePopulation function
def IndividualFitness(individual,points):

    sumFitness = 0.0
    total = 0.0
    exponent = 0

    for indexPoints in range(len(points)):
        for i in range(len(individual)): # ((1.95 + 8.16 * 1 + -2 * 12) – 5)^2 = 9.67
            sumFitness =  sumFitness + individual[i] * (points[indexPoints][0] ** exponent)
            exponent = exponent + 1

        sumFitness = (sumFitness - points[indexPoints][1])**2 
        total = total + sumFitness
        sumFitness = 0
        exponent =0 
    
    MSE = math.sqrt(float(total)/len(points))
    #Note: We used (len(points)/error) as our fitness because when we perform selection, we usually select the “fitter” chromosomes and here it represents an error and then its inverse would be the good thing to maximize
    if(MSE == 0 ):
      return 1
      
    return (float(1)/MSE)

def PopulationFitness(population,points):

    fitnessValues = []

    for i in (population):
        fitnessValues.append(IndividualFitness(i,points))

    return fitnessValues

#Here we have no faesibilty violation possible
#Step 3: Let’s select the parents! First, we apply tournament selection

def TournamentSelection(population,fitnessValues):

    matingPool = population
    
    while(len(matingPool)!=1):

        temp = []
        for i in range(len(matingPool)-1):

           index1 = random.randint(0,len(matingPool)-1)
           index2 = random.randint(0,len(matingPool)-1)

           while(index1 == index2):
              index1 = random.randint(0,len(matingPool)-1)
              index2 = random.randint(0,len(matingPool)-1)

           fitness1 = fitnessValues[index1]
           fitness2 = fitnessValues[index2]

           if(fitness1 > fitness2):
             temp.append(matingPool[index1])
           else:
             temp.append(matingPool[index2])

        matingPool = temp

    return matingPool[0]

#Step 4: Let’s perform crossover between C1 and C2:
#First, generate a random integer (Xc1) between 1 and len(C)-1 to be the crossover point and (Xc2) .
#Second, generate a random number (rc) between 0 and 1:
#If rc <= Pc, perform crossover at Xc1 and Xc2.
#If rc > Pc, no crossover. (O1 = P1 and O2 = P2)
def Crossover(parent1 ,parent2):

    rc = random.random()

    if(rc <= PC):
        XC1 = random.randint(1,len(parent1)-2)
        XC2 = random.randint(XC1 + 1 ,len(parent1)-1)
        index1 = XC1
        index2 = XC2
        temp = parent1[index1:(index2+1)]
        parent1[index1:(index2+1)] = parent2[index1:(index2+1)]
        parent2[index1:(index2+1)] = temp

    return parent1,parent2

#Step 5: Let’s perform mutation on the offspring:
#Iterate over each bit in each offspring chromosome and:
#Non_Uniform Floating Point Mutation
#  
def Mutate(child,currGeneration,maxGenerations):

    y = deltaHigh = deltaLow = 0.0
    for i in range(len(child)):
        r = random.uniform(0,1)
        if(r <= PM):
            deltaLow = child[i] - minRange
            deltaHigh = maxRange - child[i]
            r = random.uniform(0,1)
            if(r <= 0.5):
                y=deltaLow
            else:
                y=deltaHigh
            y = y * ( 1 - r**((1 - currGeneration/maxGenerations ) ** dependencyFactor ) )
            if(r <= 0.5):
                child[i] = round(child[i] - y,1)
            else:
                child[i] = round(child[i] + y,1)

    return child

#Step 6: Replace the current generation with the new offspring using any of the 
#replacement strategies explained earlier, go to step 2 and repeat the process
#Elitisit replacement: Elitist Strategy (Elitism):• It is steady-state replacement, but keep best-so-far individuals
#a number of individuals are selected to reproduce, and 
#the offspring replace their parents.
#Drawbacks: all parents of the population become almost similar over many iterations.
def Replacement(population,children,points):
    
    population.extend(children)
    fitness = PopulationFitness(population,points)
    myTuple=sorted(tuple(zip(fitness,population)))
    myTuple= myTuple[2:]
    fitness,population =  list(map(list, zip(*myTuple)))

    return population

#Mating Function takes 2 parents and returns new population
def Mating(population,fitnessValues,points,currGeneration,maxGenerations):

        parent1 = TournamentSelection(population,fitnessValues)
        parent2 = TournamentSelection(population,fitnessValues)

        #while(parent1 == parent2):
            #parent2 = RouletteWheelSelection(population,fitnessValues)
        
        parents = [parent1,parent2]  

        child1,child2 = Crossover(parent1,parent2)
        child1 = Mutate(child1,currGeneration,maxGenerations)
        child2 = Mutate(child2,currGeneration,maxGenerations)

        children = [child1,child2]

        population = Replacement(population,children,points)

        return population

#Final Optimal Function Check at last generation iteration done to take best individual
def CalcOptimal(population,fitnessValues):

    maxFitness = max(fitnessValues)

    index =0 

    for i in range(len(population)):
        if(fitnessValues[i] == maxFitness):
            index = i 
            break

    return population[index]

#PrintResult function
#You must read the input from the given file and write the output to a file. The 
#output should consist of the dataset index, the coefficients of the polynomial 
#function, and its mean square error.

def printResult(population,fitnessValues,points,TestCaseIndex):
  
    print("*************************************************************")
    print("*************************************************************")
    bestSolution = CalcOptimal(population,fitnessValues)

    print("DataSet Case Index : " + str(TestCaseIndex))

    print("The coefficients of the polynomial function are : " )
    print(bestSolution)
    print("The mean square error of this solution is : " + str(int(1/IndividualFitness(bestSolution,points))))
    print("*************************************************************")
    print("*************************************************************")

#Our FitCurve Function that calls other functions
def FitCurve(points,degree,noPoints,TestCaseIndex):

    populationSize = int(noPoints) * 20 + 500
    maxGenerations = 100

    population = InitializePopulation(populationSize,degree)
    
    for i in range(maxGenerations):

        fitnessValues= PopulationFitness(population,points)
        population = Mating(population,fitnessValues,points,i,maxGenerations)

    printResult(population,fitnessValues,points,TestCaseIndex)

#Main function that handles files
def Main(readFilePath, writeFilePath):

    readFilePath = open(readFilePath) 

    line = readFilePath.readline()

    noTestCases = int(line)

    sys.stdout = open(writeFilePath, "w")

    line = readFilePath.readline() 

    while(line):
       
       for TestCaseIndex in range(noTestCases):
           line = line.split()
           noPoints = int(line[0])
           degree = int(line[1])
           points = []
           line = readFilePath.readline()
           for  i in range(noPoints):
              line = line.split()
              point = []
              point.append(float(line[0]))
              point.append(float(line[1]))
              points.append(point)
              line = readFilePath.readline()
           
           FitCurve(points,degree+1,noPoints,TestCaseIndex)

       line = readFilePath.readline() 

    readFilePath.close()
    #sys.stdout.close()



#Let us Start our Execution here

readFilePath = "Curve_Fitting_Input.txt"

#You will have to create the file already in the path given
writeFilePath = "Curve_Fitting_Output.txt"

Main(readFilePath,writeFilePath)

