#Locality Sensitive Hashing for Data Prefetching

##How to run

We use this fork of ChampSim to evaluate our prefetching approach: https://github.com/Quangmire/ChampSim

If you want to run our source code:
1. Follow the steps in the "Building, Running, and Evaluating" for building ChampSim
2. Choose a python model file from our repo to run
3. Rename the file to model.py and replace the model.py from the ChampSim directory with our file
4. Follow the ChampSim steps for generating the prefetch file and running it

##Source Code Description
1. lsh_model.py is the base implementation.
2. bf_model.py is a bloom filter version of the "page only" variation of our basic implementation
3. oracle_model.py generates a prefetcher that issues the correct prefetches using the knowledge of the future memory accesses

Also included are scripts used for running our implemenation and saving the output nicely.
