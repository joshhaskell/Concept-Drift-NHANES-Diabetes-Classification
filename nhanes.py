import numpy as np
import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
from collections import defaultdict

def nhanes_variable_list(components=['Demographics', 'Dietary', 'Examination', 'Laboratory', 'Questionnaire']):
    """
    Scrape the NHANES variable list page for each component to return a single dataframe of all variables.
    """

    var_list_base_url = 'https://wwwn.cdc.gov/nchs/nhanes/search/variablelist.aspx?Component='
    df = pd.DataFrame()

    for component in components:
        try:
            var_list_url = var_list_base_url + component
            response = requests.get(var_list_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table', id='GridView1')
        except AttributeError:
            print('No data for ' + component)
            continue
        except Exception as e:
            print('Error' + e + ' for ' + component)
            continue
        finally:
            column_headers = [th.get_text() for th in table.find('tr').find_all('th')]
            comp_df = pd.DataFrame(columns = column_headers)
            for row in table.tbody.find_all('tr'):
                row_data = [td.get_text() for td in row.find_all('td')]
                comp_df = comp_df.append(pd.Series(row_data, index=column_headers), ignore_index=True)
            print("Load complete for component: " + component)
            comp_df['Component'] = component
            df = df.append([comp_df])
            
    return df

def var_file_name(feature_list, begin_year='1999', end_year='2018'):
    """
    Return dataframe with variable name, file name, year, and begin year for a list of variables range of years.
    """
    df = pd.DataFrame()
    var_df = nhanes_variable_list() #list of components set by default. If fewer components are needed, specify them here.
    
    for feature in feature_list:
        #check for year and feature in dataframe
        feature_df = var_df.loc[var_df['Variable Name'] == feature]
        year_feature_filter = (feature_df['Variable Name'].isin(feature_list)) & (feature_df['Begin Year'] >= begin_year) & (feature_df['EndYear'] <= end_year)
        row = feature_df[['Variable Name','Begin Year','EndYear','Data File Name','Data File Description','Component']].loc[year_feature_filter] 
        df = df.append([row]).sort_values(by=['Variable Name','Begin Year'])
        df['Year'] = df['Begin Year'] + '-' + df['EndYear']

    return df[['Variable Name','Year','Begin Year','Data File Name','Data File Description','Component']]  

def get_nhanes_data(dataframe, features):
    """
    Return dictionary of dataframes with datasets appended for a list of features.
    """
    df = pd.DataFrame()
    temp_df = dataframe.copy()
    #feature_df = temp_df.loc[temp_df['Variable Name'].isin(features)]['Variable Name'].unique() #I should not need this line
    base_url = "https://wwwn.cdc.gov/Nchs/Nhanes"
    visited_list = []
    in_visited = False
    groups_dict = defaultdict(list)
    count = 0 #unique identifier for each group of datasets

    for feature in features:
        dataset_group_num = str(count) #datasets can include multiple features, so this is a way to identify which group of datasets the features belong to
        years = temp_df.loc[temp_df['Variable Name'] == feature]['Year'].to_list()
        datasets = temp_df.loc[temp_df['Variable Name'] == feature]['Data File Name']
        for idx, dataset in enumerate(datasets):
            year = years[idx:idx+1][0]
            url = f"{base_url}/{year}/{dataset}.XPT"
            if url in visited_list:
                in_visited = True
            else:
                try:
                    dataset_df = pd.read_sas(url)
                    dataset_df['Year'] = year
                    groups_dict[dataset_group_num].append(dataset_df)
                except Exception as e:
                    print("Error - dataset: " + dataset + " not loaded for feature ", feature)
                    print("Error -", e)
                finally:
                    visited_list.append(url)
        if in_visited:
            count += 1
            in_visited = False
            print("Datasets already loaded for feature: " + feature)
            continue
        else:
            try:
                groups_dict[dataset_group_num] = pd.concat([d.set_index(['SEQN','Year']) for d in groups_dict[dataset_group_num]], axis=0, join='outer')
            except Exception as e:
                print(feature + " error: " + str(e))
            finally:
                print("Datasets loaded for feature: " + feature)
                count += 1

    return groups_dict