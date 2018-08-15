# nyc-evictions

This repo contains scripts analyzing NYC evictions data from the NYC Open Data Portal. 

The most important scipt is sanitize.py, which takes the horribly formatted addresses in the city's raw data and reforms them so that they can be geocoded using the city's GOAT API. 

The files here were used for a story on the Inwood rezoning. Read that here: http://gothamist.com/2018/08/07/inwood_rezoning_data.php

And on the data...

NYC Open Data Portal: https://opendata.cityofnewyork.us/
NYC Eviction [raw]: https://data.cityofnewyork.us/City-Government/Evictions/6z8x-wfk4/data
GOAT API: http://a030-goat.nyc.gov/goat/Default.aspx
