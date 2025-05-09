## Usage
```shell
python main.py <EXPIRY_CODE> <T1> <T2> <STRIKE1> [<STRIKE2> <STRIKE3> ...]
```
- EXPIRY_CODE: Option expiry code
- T1: Total runtime in seconds
- T2: Interval between computations in seconds
- STRIKE ...: List of strike prices of at least length 1, additional strike prices are optional
- python version is 3.12

For example: 
```shell
python main.py 23MAY25 20 5 98000 98500 99000
```
## Output: 
a results.csv file in the same directory. <br>
#### Columns:  
- timestamp,<br> 
- strike, <br>
- C (calculated call mark price),<br> 
- P (calculated put mark price), <br>
- C_ref (Deribit's call mark price, if available), <br>
- P_ref (Deribit's put mark price, if available),<br>
- C_diff (C/C_ref -1, displayed as percentage),<br>
- P_diff (P/P_ref -1, displayed as percentage).

## Key Challenges:
 - I have worked extensively in existing projects, which provides me with a template for structure, variable names setting up a project involving multiple files from scratch was new for me. I'm sure the structure is not quite optimized, but to me the organization makes sense (see following section).
 - Using a websocket api was also new for me.
 - The main difficulty in terms of logic is in determining the (implied) volatility for the calculation of mark prices. I believe there are many options, and a wide range of potential complexity that you can add here. I have kept my implementation simple, to focus on delivering a working product first, and potentially improving performance later. 
 - After calculating the mark prices, there is a lot of data hanging around in different variables. Sorting through this to decide which data is needed when and where, in what format, and how that can be accomplished as efficiently as possible is a challenge. I have not spent much time on cleaning up the code, so there are likely inefficiencies with redundant data and/or data transformations.

## Reasoning for the design and assumptions made:
The project is split in 4 files, which separately take care of:
- accounting (main.py): taking in arguments and passing these on, collecting results and manipulating these for export.
- scheduling (run_scheduler.py): ensuring that every t2 seconds a new calculation occurs, until t1 seconds have passed. 
- data collection (market_data.py): connecting to the api and supplying current market data when needed.
- calculations (calculate_mark_price.py): manipulating and transforming market data to calculate mark prices.

The choices made in calculate_mark_price.py have the most influence on the output. The main variable that is challenging to aquire in the calculation of mark prices for unlisted strikes is implied volatility. I have decided to fit a line through iv's for existing strike prices using a cubic function. Specifically, I lump together all bid and aks iv's for puts and calls, because 1) fitting a line through combined bid and ask iv's should result in a fitted iv that lies roughly/mostly between the bid and ask iv's, such that this can immediately be used to calculate a midpoint price, which will be my mark price, and 2) because the iv for puts and calls of a given strike and expiration should theoretically be equal, so adding these together should result in a better estimation of parameters. A major assumption of (1) is that the iv of the mark price (and thus the mark price itself) should in general lie between that of the bids and asks. I have chosen a cubic function becuase it is easy to implement, while providing a not-horrible fit. Before actually estimating the parameters of the cubic function, I trim datapoints with high and low strike prices, and with much higher iv than average (trim amounts are hardcoded). This is an easy (but crude) way of weighting strikes close to the value of the underlying, which provide more accurate iv's. <br>
<br>
There are several instances of averaging for convenience. The market data is not always supplied at exactly the same moment for a single iteration, so at some point I take the average of the underlying, the interest rate, and the timestamp. The differences are very small, but this is a quick fix that I think is acceptable in this setting (I would not find it acceptable in Deribit's production environment, for example). Another challenge would then be to ensure perfect synchronicity of market data, or somehow deal with this asynchronicity in a structured and substantiated way.  <br>
Using BTC is currently hardcoded, although I have tried to include optional argument in various functions that should facilitate easier reformatting to a situation where the currency can be given as an argument. 
