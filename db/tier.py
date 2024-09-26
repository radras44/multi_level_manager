def promediar (arr: list) : 
    result = 0
    for el in arr : 
        result += el
    
    return result / len(arr)

print(promediar([4,4,7,7.2,7.1111111111111]))