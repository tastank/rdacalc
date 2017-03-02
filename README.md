# rdacalc
Reverse density altitude calculator - calculates where density altitude equals a specified altitude using the HRRR model

Stemming from a discussion a few years ago regarding trying to fly to the top of Class E (17,999ft MSL)
in a Cessna 152 on a particularly cold day (which turned out not to be the way to do it) and my experience
writing weather ETL for Understory, this "reverse density altitude calculator" calculates the height where
density altitude equals a specified true altitude based on temperature and geopotential height values from
the 0-3 hour HRRR forecasts. 
