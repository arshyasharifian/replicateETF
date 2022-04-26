# open csv file
# count the number of holdings
import pandas as pd

def extractData():
    payload = {}
    
    df = pd.read_csv('test.csv')
    df = df.transpose()

    payload['NumberOfHoldings'] = len(df.index)

    print(df.columns)

    # marks_list = df['Marks'].tolist()
    
    #extract and isolate the ticker and percentage



    return payload

payload = extractData()
print(payload)



    