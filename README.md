# Real Estate Data Processing
## Project for Data Processing in Python (JEM207)
## Vojtěch Kania, Lukáš Novotný

## Project summary

This project aims to automate scraping data from [sreality](https://www.sreality.cz/) using its public [API](https://www.sreality.cz/api/cs/v2/estates?).
We have developed an installable package for this purpose. Tutorial/Example of use with comments can be found ...
Moreover, we have created an exemplary EDA which we performed on flats for sale category. Can be found in EDA - flats for sale folder with SQLite containing the data. Data were downloaded using our source code. The EDA was done before the last version of package was finished. The purpose of the EDA notebook is to show users an example how to process this kind of data. Nevertheless, the EDA would differ for different categories (different columns) as well as for different data (different outliers/misisng values treatment).

TO DO:

- dodělat dokumentaci


![Our Architecture with DB](scraper_of_sreality.cz.png)
