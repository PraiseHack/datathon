# datathon
This is a simple ETL for Nigerian educational system.

The setup is as simple as it could be. 
First is my docker compose file that has scripts for airflow and postgres services.

A database for this project was created and also its schema with different tables using an init.sql script.

The ETL implementation was through a simple dag that extract a csv file from my local machine using pandas, transforming the csv file and finally loading it to the postgres database where it was made available for the data scientist and analyst.

Tech stack used were postgres, docker and airflow.

