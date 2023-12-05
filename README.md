# Shoeboxing-algorithm
This repository contains the script of the implementation of a simplification shoeboxing algorithm for Urban and Building Energy Modeling. The algorithm coverts a building of any shape into a representative shoebox to speed-up the simulation task of Urban and Building Energy Modeling, as shown in the figure below:
![SimplificationWorkflow](https://github.com/fbattini/Shoeboxing-algorithm/assets/71373172/7134c6ea-a882-4be8-8794-db37d2a836d1)
The algorithm starts from an .idf file to perform the simplification. An example of the .idf structure can be found in the Simulation/Detailed folder. The final structure of the Simulation folder in which the algorithm runs is reported in the Simulation_Done folder.
The file to run to perform the simplification is 1_DetailedToSimplified.py.
The technical implementation of the algorithm is in the Python programming language and is based on numpy, pandas, scipy, and eppy.
# More details and references
To learn more about this work or to cite it, please see the following two publications:
- Validation of the algorithm for stand-alone buildings: https://www.sciencedirect.com/science/article/pii/S2210670722006096
- Validation of the algorithm at district-level (open access): https://www.sciencedirect.com/science/article/pii/S0306261923009340
# Contact
[Federico Battini](https://www.linkedin.com/in/federico-battini/).
