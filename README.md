# Shoeboxing-algorithm
This repository contains the script of the implementation of a simplification shoeboxing algorithm for Urban and Building Energy Modeling. The algorithm coverts a building of any shape into a representative shoebox to speed-up the simulation task of Urban and Building Energy Modeling, as shown in the figure below:
![SimplificationWorkflow](https://github.com/fbattini/Shoeboxing-algorithm/assets/71373172/7134c6ea-a882-4be8-8794-db37d2a836d1)
The algorithm starts from an .idf file to perform the simplification. An example of the .idf structure can be found in the Simulation/Detailed folder. The final structure of the Simulation folder in which the algorithm runs is reported in the Simulation_Done folder.

The file to run to perform the simplification is 1_DetailedToSimplified.py. The whole process is performed automatically for as many .idf files as there are in the Simulation/Detailed folder.

The technical implementation of the algorithm is in the Python programming language and is based on numpy, pandas, scipy, and eppy.
## More details and references
To learn more about this work or to cite it, please see the following two publications (the second is open access):
- Federico Battini, Giovanni Pernigotto, Andrea Gasparella, "A shoeboxing algorithm for urban building energy modeling: Validation for stand-alone buildings", Sustainable Cities and Society, Volume 89, 2023, 104305, ISSN 2210-6707, https://doi.org/10.1016/j.scs.2022.104305. (https://www.sciencedirect.com/science/article/pii/S2210670722006096)
- Federico Battini, Giovanni Pernigotto, Andrea Gasparella, "District-level validation of a shoeboxing simplification algorithm to speed-up Urban Building Energy Modeling simulations", Applied Energy, Volume 349, 2023, 121570, ISSN 0306-2619, https://doi.org/10.1016/j.apenergy.2023.121570. (https://www.sciencedirect.com/science/article/pii/S0306261923009340)
## Current limitations
For now, this version of the algorithm implementation has the following limitations:
- Detailed models must be run for comparison and to obtain some properties to create the simplified models
- Buildings can have up to four stories
- Results are not automatically post-processed

These limitations are only related to the practical implementation and not to the methodology itself.
## Contact
[Federico Battini](https://www.linkedin.com/in/federico-battini/)
