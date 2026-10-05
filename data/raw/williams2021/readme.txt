This .txt file was generated on 2021-03-25 by Nathan Williams

GENERAL INFORMATION

1. Title of Dataset: 
	Scaling the extinction vortex: Body size as a predictor 	of population dynamics close to extinction events.

2. Author Information: [Principal Investigator Contact 		Information]
	Name: Nathan Williams
	Institution: University of Bristol
	Address: School of Biological Sciences, 24 		Tyndall Avenue, BS8 1TQ
	Email: nathan.williams.mail@gmail.com

3. Date of data collection (single date, range, approximate date): 
	2020-06-10:2021-03-18 

4. Geographic location of data collection: 
	University of Bristol

5. Keywords:
	Biological sciences

6. Language information: 
	English 


SHARING/ACCESS INFORMATION

1. Licenses/restrictions placed on the data: 
	Four time series used in the analyses are confidential 	and cannot be made publicly available.

2. Was data derived from another source? Yes
	A. If yes, list source(s): The Living Planet Database 	(https://livingplanetindex.org/home/index)

3. Recommended citation for this dataset: 
	Williams NF, McRae L, Freeman R, Capdevila P & Clements 	CF (2021) Data from: Scaling the extinction vortex: 	Body size as a predictor of population dynamics close 	to extinction events. Dryad Digital Repository. 	https://doi.org/10.5061/dryad.jwstqjq8c

DATA & FILE OVERVIEW

1. File List: 

	1. BayesianAnalyses.R: R code to fit hierarchical 	bayesian models to the outputs from the state-space 
	models.
	
	2. Humbert_function.R: Functions from Humbert et al. 	2009.

	3. StateSpace.R: R code to estimate the population 	change using state-space models.

	4. phylogeny.tre: A phylogenetic tree of the species in 	the dataset.

	5. population_data.csv: Raw population abundance data 	to be put into the state-space models (i.e. 		StateSpace.R). Date of creation: 2021-03-23.

	6. modelling_data.csv: Data to be used in the models 	(i.e., BayesianAnalyses.R). Date of creation: 		2021-03-23.

2. Relationship between files, if important: 

	1. BayesianAnalyses.R: Requires phylogeny.tre & 	modelling_data.csv.

	2. StateSpace.R: Requires Humbert_function.R &
	population.csv.

3. Are there multiple versions of the dataset? 
	No


METHODOLOGICAL INFORMATION

1. Description of methods used for collection/generation of data: 	We obtained time series data of populations monitored 	to extirpation from: i) the Living Planet Database 	(LPD), a global database containing annual population 	abundance data for over 25,000 vertebrate populations 	between 1950-2019 and ii) from previously published 	work on the extinction vortex (Fagan & Holmes, 2006; 	Ecology Letters). A diverse range of methods to monitor 	population abundance are included in the LPD with the 	caveat for inclusion of time series being that 		monitoring should be reputable, appropriate for the 	species and consistent through time (Loh et al., 2005; 	Phil. Trans. R. Soc. B). We obtained body size and 	life history data for each species from the amniotes 	life history database (Myhrvold et al., 2015; Ecology).

2. Methods for processing the data: 
	We filtered the LPD for time series satisfying a number 	of criteria, as outlined in the main manuscript. We 	joined the population data to the life history data 	using SQL.

3. Instrument- or software-specific information needed to interpret the data: 
	An up-to-date version of the R statistical programming 	language is required to run the code. All required 	packages are listed in the R files.


DATA-SPECIFIC INFORMATION FOR: [population_data.csv]

1. Number of variables: 
	83

2. Number of cases/rows: 
	31

3. Variable List: 
	ID: Unique number for a given time series
	Binomial: Species name
	Class: Taxonomic class
	Order: Taxonomic order
	Family: Taxonomic family
	Genus: Taxonomic genus
	Species: Taxonomic species
	Common_name: Common name of the species
	Country: Country of time series origin
	System: Environmental system i.e., terrestrial, 	freshwater or marine
	Units: Units of population abundance
	Data_type: Nature of the data collection method
	1950:2020: Raw population abundance in each given year 	('NULL' where data is missing)

4. Missing data codes: 
	See 3.


DATA-SPECIFIC INFORMATION FOR: [modelling_data.csv]

1. Number of variables: 
	16

2. Number of cases/rows: 
	442

3. Variable List: 
	ID: Unique number for a given time series
	Binomial: Species name
	Class: Taxonomic class
	Order: Taxonomic order
	Family: Taxonomic family
	Genus: Taxonomic genus
	Species: Taxonomic species
	Common_name: Common name of the species
	Country: Country of time series origin
	System: Environmental system i.e., terrestrial, 	freshwater or marine
	Units: Units of population abundance
	Data_type: Nature of the data collection method
	Pred.N: Smoothed population abundance from the state-	space model
	R_t: Population growth rate calculated using parameters 	from the state-space model
	years_to_extinction: Number of years before population 	extirpation
	geometric_growth_rate: Geometric growth rate of the 	population [ln(Nt/Nt+1)]. Cells are empty where data 	is missing.
	log10_adult_body_mass_kg: Logged (base 10) adult body 	mass in kg.	

4. Missing data codes: 
	See 3.



