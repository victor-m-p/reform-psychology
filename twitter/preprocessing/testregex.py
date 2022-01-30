import re 
import pandas as pd 

# testing regex for retweets (not necessary it seems): 
reg = "@(\w+)"
str = ["RT @Calimaq: [Billet S.I.Lex] @bing", "RT @zikkonnect: The Eastern Rese"]

for i in str: 
    print(i)
    match = re.search(reg, i)[1]
    print(match)

'''
works well. 
we can always count on this setup (starting with RT @...)
and we just take the first one. 
'''

# testing regex for getting 
s = "@tudelftlibrary @sciencecentre @OpticaDelft @TNWTUDelft @tudelft Finally! Time to visit exhibition @OpticaDelft and @tudelftlibrary. Two more"
test = "|".join(list(dict.fromkeys(re.findall(r"(?<![@\w])@(\w{1,25})", s))))
test