# test
football
API:

API initial Url: https://api.football-data.org/

API account name: testing.data999@gmail.com

API token information:

Please modify your client to use a HTTP header named "X-Auth-Token" with the underneath personal token as value. Your token: 12abfbaacdab48bc8948ed6061925e1f

# How to run these programs
## Get data from API then save it as CSV
Run ```python step1_getcsv.py```  
The script retrieves data from football-data.org and saves the raw data as a CSV file named ```premier_league_stats.csv``` in the root directory.
![image](https://github.com/user-attachments/assets/22c3e7bb-c9a5-421b-8ee4-9f1dac175134)

## Clean the data and save the summaries as graphs
Run ```python step2_summarize.py```  
The script read data from CSV file, validate years, Clean the data by handling missing values using median imputation, then sort dataframe and save data as graphs in the fold ```/premier_league_plots```.
![image](https://github.com/user-attachments/assets/3f6f1878-ad7c-4b84-be00-c39dec0eeae7)
As a result of the data summary, six graphs have been generated with the following names:
* "premier_league_plots\won_by_team_and_year.png",
* "premier_league_plots\draw_by_team_and_year.png",
* "premier_league_plots\lost_by_team_and_year.png",
* "premier_league_plots\goalsFor_by_team_and_year.png",
* "premier_league_plots\goalsAgainst_by_team_and_year.png".

## graphs
![won_by_team_and_year](https://github.com/user-attachments/assets/7c9f3475-89d9-43fe-9605-f1f35485b011)


Folder structure:  
![image](https://github.com/user-attachments/assets/41633cfd-0362-4448-8e70-756d6a82d899)
