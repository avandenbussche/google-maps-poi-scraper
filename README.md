# Google Maps POI Scraper

Scrapes points of interest (POIs) from Google Maps using the Google Places API and saves them into a SQLite database. It divides a region into circular search zones and uses a search-by-radius to get the POIs in that zone. The Places API returns a max of 60 POIs per radius (20 POIs over 3 requests) so if 60 POIs were found, the circular zone was subdivided into many smaller zones. Sometimes, the Places API would return over 60 POIs for a ridicuously small radius (e.g. 4 metres) in which case the circular zone was labeled as `DENSE`. 

This program was quickly developed for a math project in Grade 12 (May 2018) and probably should not be used for anything important!