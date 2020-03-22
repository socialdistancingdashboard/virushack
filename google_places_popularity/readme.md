#Google places
get_place_id.py holt sich aus verschiedenen großen Städten alle Bus/Bahnstationen und schaut für welche es popularity gibt, und speichert das dann in einer csv ab.

scraper.py holt sich von Google Maps für die Orte die Popularity und speichert sie im S3 Bucket. - Stündlich

aggregator.py fasst Daten für einen Tag zusammen und averaged die Werte + Extrahiert die PLZ

##TODO
Es braucht noch ein Skript was dann auf die CSV zugreift und für alle die Popularität downloaded und es im AWS speichert.
