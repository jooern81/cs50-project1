# -*- coding: utf-8 -*-
"""
Created on Sat Sep 12 17:12:07 2020

@author: chinjooern
"""

import psycopg2
import pandas as pd
from sqlalchemy import create_engine, select, MetaData, Table
import os
import random
from random import choice

host = "ec2-35-172-73-125.compute-1.amazonaws.com"
database = "d6bt7imri7f5k9"
user = "bbilcrjmdqsefb"
port = "5432"
password = "1792ea62a0f1684cafa24359decd4d31df2ac7f7a2bcf4bf9f86aad8254f5f2f"
URI = "postgres://bbilcrjmdqsefb:1792ea62a0f1684cafa24359decd4d31df2ac7f7a2bcf4bf9f86aad8254f5f2f@ec2-35-172-73-125.compute-1.amazonaws.com:5432/d6bt7imri7f5k9"
# Heroku CLI
# heroku pg:psql postgresql-silhouetted-61094 --app supermarketsimulator

engine = create_engine('postgres://bbilcrjmdqsefb:1792ea62a0f1684cafa24359decd4d31df2ac7f7a2bcf4bf9f86aad8254f5f2f@ec2-35-172-73-125.compute-1.amazonaws.com:5432/d6bt7imri7f5k9')
meta = MetaData()

def connect_to_database():
    try:
        connection = psycopg2.connect(user = user,
                                      password = password,
                                      host = host,
                                      port = port,
                                      database = database)
        
    except (Exception, psycopg2.Error) as error:
            print("Error while connecting to PostgreSQL", error)
            
    return connection

#the csv to be added must not contain any '(' , ')' , '/', this affects the calling of the table columns downstream

def add_df_to_db(CSV_NAME,folder_name): #based on the CSV name, the CSV will be saved as a dataframe which will be converted to a table
    connection = connect_to_database()
    df = pd.read_csv(CSV_NAME) #CSV name format must be "xxxx.csv, STRICTLY LOWER CASE"
    TABLE_NAME = CSV_NAME.split(folder_name)[-1][1:]
    print(TABLE_NAME)
    TABLE_NAME = TABLE_NAME.split(".")[0] + "_table"
    
    existing_table_names = []
    database_table_tuple = check_database_tables()
    for table_tuple in database_table_tuple:
        for table_name in table_tuple:
            existing_table_names.append(table_name)
            
    
    if TABLE_NAME in existing_table_names:
        print(TABLE_NAME + ' already exists in the database.')
        
    else:
        df.to_sql(TABLE_NAME,con=engine,dtype=None)
        print(df)
        cursor = connection.cursor() #print some of the newly added table's details
        postgreSQL_select_Query = "select * from {}".format(TABLE_NAME)
        cursor.execute(postgreSQL_select_Query)
        print(TABLE_NAME + " has been added to the database.")
        print(cursor.fetchall())
        cursor.close()
        connection.close()
    
def add_df_to_db2(EXCEL_NAME,folder_name): #based on the excel name, the excel will be saved as a dataframe which will be converted to a table
    connection = connect_to_database()
    df = pd.read_excel(EXCEL_NAME) #CSV name format must be "xxxx.xlsx, STRICTLY LOWER CASE"
    TABLE_NAME = EXCEL_NAME.split(folder_name)[-1][1:]
    print(TABLE_NAME)
    TABLE_NAME = TABLE_NAME.split(".")[0] + "_table"
 
    existing_table_names = []
    database_table_tuple = check_database_tables()
    for table_tuple in database_table_tuple:
        for table_name in table_tuple:
            existing_table_names.append(table_name)
            
    
    if TABLE_NAME in existing_table_names:
        print(TABLE_NAME + ' already exists in the database.')
        
    else:
        df.to_sql(TABLE_NAME,con=engine,dtype=None)
        print(df)
        cursor = connection.cursor() #print some of the newly added table's details
        postgreSQL_select_Query = "select * from {}".format(TABLE_NAME)
        cursor.execute(postgreSQL_select_Query)
        print(TABLE_NAME + " has been added to the database.")
        print(cursor.fetchall())
        cursor.close()
        connection.close()
    
def add_all_df_to_db(data_dir): #in a specified folder directory 'data_dir', enter all subfolders and convert all csv files to dfs to be uploaded to the database
    subdirs = [x[0] for x in os.walk(data_dir)]  
    main_dir = subdirs[0]
    subdirs = subdirs[1:]
                                                                      

    for folder in subdirs:
        print('Folder name: ' +  folder)
        filenames = os.walk(folder).__next__()[2]
        for filename in filenames:
            if '.csv' in filename:
                CSV_NAME = os.path.join(folder,filename)
                print('CSV name: ' + CSV_NAME)
                add_df_to_db(CSV_NAME,folder)
                
    for folder in subdirs:
        print('Folder name: ' +  folder)
        filenames = os.walk(folder).__next__()[2]
        for filename in filenames:
            if '.xlsx' in filename:
                XLS_NAME = os.path.join(folder,filename)
                print('XLS name: ' + XLS_NAME)
                add_df_to_db2(XLS_NAME,folder)

    return

    
def clone_table_in_db(TABLE_NAME, CLONE_NAME): #based on the CSV name, the CSV will be saved as a dataframe which will be converted to a table
    connection = connect_to_database()
    cursor = connection.cursor()
    s = ""
    s += "CREATE TABLE"
    s += " " + CLONE_NAME
    s += " AS ("
    s += "SELECT"
    s += " *"
    s += " FROM " + TABLE_NAME
    # s += " WHERE product = 'Milk'" #insert a condition to filter the table being cloned
    s += " );"
    # execute the copy table SQL
    cursor.execute(s)
    # # if autocommit is off:
    #connection.commit()
    
    #print some of the newly added table's details
    #cursor = CONNECTION.cursor() 
    postgreSQL_select_Query = "select * from {}".format(CLONE_NAME)
    cursor.execute(postgreSQL_select_Query)
    print(CLONE_NAME + " has been cloned to the database.")
    # print(cursor.fetchall())
    cloned_table = cursor.fetchall()
    cursor.close()
    connection.commit()
    print(cloned_table)
    return(cloned_table)
    
def select_table_columns(table_name, column_names): #column names is a list of columns you want to select
    connection = connect_to_database()
    cursor = connection.cursor()
    s = ""
    s += "SELECT "
    for column_name in column_names:
        s += " " + column_name + ','
    s = s[:-1]
    s += " FROM " + table_name
    s += ";"
    print(s)
    # execute the copy table SQL
    cursor.execute(s)
    columns = cursor.fetchall()
    print(columns)
    cursor.close()
    connection.close()
    return(columns)

def update_table_column(table_name,column_name, modifier_value, modifier_type ='add'): #modifier, does add, subtract, divide, multiply
    connection = connect_to_database()
    cursor = connection.cursor()
    s = ""
    s += "UPDATE "
    s += table_name + " "
    s += "SET "
    s += column_name + " = " + column_name
    if modifier_type == 'add':
        s += '+' + str(modifier_value)
    if modifier_type == 'multiply':   
        s += '*' + str(modifier_value)
    s += " WHERE "
    s += column_name + " != 0" 
    s += ";"
    print(s)
    # execute the copy table SQL
    cursor.execute(s)
    connection.commit()
    postgreSQL_select_Query = "select {}".format(column_name)
    postgreSQL_select_Query += " from {}".format(table_name)
    cursor.execute(postgreSQL_select_Query)
    print(table_name + " has been updated.")
    # print(cursor.fetchall())
    updated_table = cursor.fetchall()
    cursor.close()
    connection.commit()
    print(updated_table)
    cursor.close()
    return(updated_table)
    
def render_table_from_database(table_name):
    connection = connect_to_database()
    cursor = connection.cursor() #print some of the newly added table's details
    postgreSQL_select_Query = "select * from {}".format(table_name)
    cursor.execute(postgreSQL_select_Query)
    print(cursor.fetchall())
    cursor.close()
    connection.close()
        
def check_database_tables():
    database_table_tuple = tuple(engine.execute("SELECT * FROM pg_catalog.pg_tables WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema' ORDER BY pg_tables.tablename").fetchall())
    print(database_table_tuple)
    return(database_table_tuple)

def get_columns_names(table_name):
    connection = connect_to_database()
    cursor = connection.cursor()
    cursor.execute("Select * FROM {} LIMIT 0".format(table_name))
    num_fields = len(cursor.description)
    field_names = [i[0] for i in cursor.description]
    colnames = [desc[0] for desc in cursor.description]
    print(colnames)
    cursor.close()
    num_fields = len(cursor.description)
    return(colnames)
    
def add_own_table_columns(table_name, old_column_name, new_column_name):
    connection = connect_to_database()
    cursor = connection.cursor()
    postgreSQL_select_Query = "ALTER TABLE {}".format(table_name)
    postgreSQL_select_Query += " ADD {} ".format(new_column_name)
    postgreSQL_select_Query += " real"
    cursor.execute(postgreSQL_select_Query)
    connection.commit()
    connection.close()
    
    connection = connect_to_database()
    cursor = connection.cursor()
    postgreSQL_select_Query = "UPDATE {}".format(table_name)
    postgreSQL_select_Query += " SET {} =".format(new_column_name)
    postgreSQL_select_Query += " {}".format(old_column_name)
    cursor.execute(postgreSQL_select_Query)
    connection.commit()
    connection.close()
    
    connection = connect_to_database()
    cursor = connection.cursor()
    s = ""
    s += "SELECT "
    s += new_column_name
    s += " FROM " + table_name
    s += ";"
    print(s)
    # execute the copy table SQL
    cursor.execute(s)
    new_column = cursor.fetchall()
    cursor.close()
    connection.close()
    print(new_column)
    
    return(new_column)

def add_other_table_columns(table_name, other_table_name, other_column_name, new_column_name):
    connection = connect_to_database()
    cursor = connection.cursor()
    postgreSQL_select_Query = "ALTER TABLE {}".format(table_name)
    postgreSQL_select_Query += " ADD {} ".format(new_column_name)
    postgreSQL_select_Query += " real"
    cursor.execute(postgreSQL_select_Query)
    connection.commit()
    connection.close()
    
    connection = connect_to_database()
    cursor = connection.cursor()
    postgreSQL_select_Query = "UPDATE {}".format(table_name)
    postgreSQL_select_Query += " SET {} = (".format(new_column_name)
    postgreSQL_select_Query += "SELECT {} ".format(other_column_name)
    postgreSQL_select_Query += "FROM {} ".format(other_table_name)
    postgreSQL_select_Query += "WHERE {}.index ".format(other_table_name)
    postgreSQL_select_Query += "= {}.index );".format(table_name)
    print(postgreSQL_select_Query)
    cursor.execute(postgreSQL_select_Query)
    connection.commit()
    connection.close()
    
    connection = connect_to_database()
    cursor = connection.cursor()
    s = ""
    s += "SELECT "
    s += new_column_name
    s += " FROM " + table_name
    s += ";"
    print(s)
    # execute the copy table SQL
    cursor.execute(s)
    new_column = cursor.fetchall()
    cursor.close()
    connection.close()
    print(new_column)
    
    return(new_column)

#insert data into specific column of table based on index
def insert_data_into_table_column(table_name,column_name,input_data):
    connection = connect_to_database()
    cursor = connection.cursor()
    postgreSQL_select_Query = "INSERT INTO {} ".format(table_name)
    postgreSQL_select_Query += "(index,{})".format(column_name) #the columns being referenced
    postgreSQL_select_Query += " VALUES (%s,%s)" #input data in the form[(index1,value1),(index2,value2)]
    cursor.executemany(postgreSQL_select_Query,input_data)
    connection.commit()
    connection.close()
    
    
    connection = connect_to_database()
    cursor = connection.cursor()
    s = ""
    s += "SELECT "
    s += column_name
    s += " FROM " + table_name
    s += ";"
    print(s)
    # execute the copy table SQL
    cursor.execute(s)
    edited_column = cursor.fetchall()
    cursor.close()
    connection.close()
    print(edited_column)
    
#update data in specific column of table based on index
#input data should have value followed by index
def update_data_in_table_column(table_name,column_name,input_data):
    connection = connect_to_database()
    cursor = connection.cursor()
    postgreSQL_select_Query = "UPDATE {} ".format(table_name)
    postgreSQL_select_Query += "SET {} = %s ".format(column_name) #the column being updated
    postgreSQL_select_Query += "WHERE index = %s" #the row being updated
    cursor.executemany(postgreSQL_select_Query,input_data)
    connection.commit()
    connection.close()
    
    
    connection = connect_to_database()
    cursor = connection.cursor()
    s = ""
    s += "SELECT "
    s += column_name
    s += " FROM " + table_name
    s += ";"
    print(s)
    # execute the copy table SQL
    cursor.execute(s)
    edited_column = cursor.fetchall()
    cursor.close()
    connection.close()
    print(edited_column)
    
#update data in specific column of table based on product
#input data should have value followed by product name
def update_data_in_table_column2(table_name,column_name,input_data):
    connection = connect_to_database()
    cursor = connection.cursor()
    postgreSQL_select_Query = "UPDATE {} ".format(table_name)
    postgreSQL_select_Query += "SET {} = %s ".format(column_name) #the column being updated
    postgreSQL_select_Query += "WHERE product = %s" #the row being updated
    cursor.executemany(postgreSQL_select_Query,input_data)
    connection.commit()
    connection.close()
    
    
    connection = connect_to_database()
    cursor = connection.cursor()
    s = ""
    s += "SELECT "
    s += column_name
    s += " FROM " + table_name
    s += ";"
    print(s)
    # execute the copy table SQL
    cursor.execute(s)
    edited_column = cursor.fetchall()
    cursor.close()
    connection.close()
    print(edited_column)
    

    
#a specific function for randomizing the basedata_demandforecast_table' - assumes it is in the db
def randomize_demand_forecast(demand_forecast_base):
    table_name = demand_forecast_base
    column_names = get_columns_names(demand_forecast_base)
    for column_name in column_names:
        if column_name != 'index' and column_name != 'product':
            update_table_column(table_name, column_name, random.randint(950,1050)/1000 , 'multiply')
    render_table_from_database(demand_forecast_base)
    
def select_specific_entry(table_name, data_column, filtering_column, column_filter): #data column = column containing data, filtering_column = column containing filter condition, column_filter = the filter
    connection = connect_to_database()
    cursor = connection.cursor()
    s = ""
    s += "SELECT "
    s += data_column + ',' + filtering_column
    s += " FROM " + table_name
    s += ";"
    print(s)
    # execute the copy table SQL
    cursor.execute(s)
    columns = cursor.fetchall()
    # print(columns)
    entry_match = [item for item in columns if column_filter in item][0][0]
    print(entry_match)
    cursor.close()
    connection.close()
    return(entry_match)

#make sure you clone the tables affected by events at some earlier point before referencing them first - all event based data is stacked in the event_xxxx_table
#this is because some events change the data but the table shown is the original
#make sure you call this function with the correct desired probability
#called_events is a list (prevents events from being called repeatedly)
def newsandevents_trigger(current_quarter,called_events):
    
    event_roll = choice([i for i in range(1,20) if i not in called_events]) #randomly roll for event 1-20, called_events is a list e.g.: [1,5,20]

    if event_roll == 1:
        frozen_pork_price = select_specific_entry('basedata_supplierquotes_table', 'selling_price', 'product', 'frozen_pork')
        event_frozen_pork_price = int(float(frozen_pork_price)*1.8)
        update_data_in_table_column2('event_supplierquotes_table', 'selling_price', [(event_frozen_pork_price,'frozen_pork')])
        
        frozen_pork_leadtime = select_specific_entry('basedata_supplierquotes_table', 'selling_price', 'product', 'frozen_pork')
        event_frozen_leadtime = int(frozen_pork_leadtime)+1
        update_data_in_table_column2('event_supplierquotes_table', 'lead_time_express', [(event_frozen_leadtime,'frozen_pork')])
                                                                                            
        frozen_pork_demand = select_specific_entry('basedata_demandforecast_table', current_quarter, 'product', 'frozen_pork') #current_quarter takes the form e.g. q1_20x1
        event_frozen_pork_demand = int(float(frozen_pork_demand)*0.8)
        update_data_in_table_column2('event_demandforecast_table', current_quarter, [(event_frozen_pork_demand,'frozen_pork')])
        
        fresh_pork_price = select_specific_entry('basedata_supplierquotes_table', 'selling_price', 'product', 'fresh_pork')
        event_fresh_pork_price = int(float(fresh_pork_price)*1.8)
        update_data_in_table_column2('event_supplierquotes_table', 'selling_price', [(event_fresh_pork_price,'fresh_pork')])
        
        fresh_pork_leadtime = select_specific_entry('basedata_supplierquotes_table', 'selling_price', 'product', 'fresh_pork')
        event_frozen_leadtime = int(fresh_pork_leadtime)+1
        update_data_in_table_column2('event_supplierquotes_table', 'lead_time_express', [(event_frozen_leadtime,'fresh_pork')])
                                                                                            
        fresh_pork_demand = select_specific_entry('basedata_demandforecast_table', current_quarter, 'product', 'fresh_pork') #current_quarter takes the form e.g. q1_20x1
        event_fresh_pork_demand = int(float(fresh_pork_demand)*0.8)
        update_data_in_table_column2('event_demandforecast_table', current_quarter, [(event_fresh_pork_demand,'fresh_pork')])
        
        called_events.append(1)
    
    if event_roll == 2:                         
        flour_demand = select_specific_entry('basedata_demandforecast_table', current_quarter, 'product', 'flour') #current_quarter takes the form e.g. q1_20x1
        event_flour_demand = int(float(flour_demand)*0.7)
        update_data_in_table_column2('event_demandforecast_table', current_quarter, [(event_flour_demand,'flour')])
        
        beer_demand = select_specific_entry('basedata_demandforecast_table', current_quarter, 'product', 'beer') #current_quarter takes the form e.g. q1_20x1
        event_beer_demand = int(float(beer_demand)*0.6)
        update_data_in_table_column2('event_demandforecast_table', current_quarter, [(event_beer_demand,'beer')])

        muesli_demand = select_specific_entry('basedata_demandforecast_table', current_quarter, 'product', 'muesli') #current_quarter takes the form e.g. q1_20x1
        event_muesli_demand = int(float(muesli_demand)*0.75)
        update_data_in_table_column2('event_demandforecast_table', current_quarter, [(event_muesli_demand,'muesli')])

        pasta_demand = select_specific_entry('basedata_demandforecast_table', current_quarter, 'product', 'pasta') #current_quarter takes the form e.g. q1_20x1
        event_pasta_demand = int(float(pasta_demand)*0.75)
        update_data_in_table_column2('event_demandforecast_table', current_quarter, [(event_pasta_demand,'pasta')])
        
        called_events.append(2)

    if event_roll == 3 and current_quarter == 4:                         
        wines_demand = select_specific_entry('basedata_demandforecast_table', current_quarter, 'product', 'wines') #current_quarter takes the form e.g. q1_20x1
        event_wines_demand = int(float(wines_demand)*1.2)
        update_data_in_table_column2('event_demandforecast_table', current_quarter, [(event_wines_demand,'wines')])

        spirits_demand = select_specific_entry('basedata_demandforecast_table', current_quarter, 'product', 'spirits') #current_quarter takes the form e.g. q1_20x1
        event_spirits_demand = int(float(spirits_demand)*1.2)
        update_data_in_table_column2('event_demandforecast_table', current_quarter, [(event_spirits_demand,'spirits')])
        
        beer_demand = select_specific_entry('basedata_demandforecast_table', current_quarter, 'product', 'beer') #current_quarter takes the form e.g. q1_20x1
        event_beer_demand = int(float(beer_demand)*1.2)
        update_data_in_table_column2('event_demandforecast_table', current_quarter, [(event_beer_demand,'beer')])

        prime_beef_demand = select_specific_entry('basedata_demandforecast_table', current_quarter, 'product', 'prime_beef') #current_quarter takes the form e.g. q1_20x1
        event_prime_beef_demand = int(float(prime_beef_demand)*1.2)
        update_data_in_table_column2('event_demandforecast_table', current_quarter, [(event_prime_beef_demand,'prime_beef')])

        called_events.append(3)

    if event_roll == 4:   
        update_table_column('event_supplierquotes_table', 'setup_costs_express', 1.2, 'multiply')
        
        called_events.append(4)
        
    if event_roll == 5:                         
        prime_beef_demand = select_specific_entry('basedata_demandforecast_table', current_quarter, 'product', 'prime_beef') #current_quarter takes the form e.g. q1_20x1
        event_prime_beef_demand = int(float(prime_beef_demand)*1.3)
        update_data_in_table_column2('event_demandforecast_table', current_quarter, [(event_prime_beef_demand,'prime_beef')])

        fresh_poultry_parts_demand = select_specific_entry('basedata_demandforecast_table', current_quarter, 'product', 'fresh_poultry_parts') #current_quarter takes the form e.g. q1_20x1
        event_fresh_poultry_parts_demand = int(float(fresh_poultry_parts_demand)*1.15)
        update_data_in_table_column2('event_demandforecast_table', current_quarter, [(event_fresh_poultry_parts_demand,'fresh_poultry_parts')])

        fresh_pork_demand = select_specific_entry('basedata_demandforecast_table', current_quarter, 'product', 'fresh_pork') #current_quarter takes the form e.g. q1_20x1
        event_fresh_pork_demand = int(float(fresh_pork_demand)*1.15)
        update_data_in_table_column2('event_demandforecast_table', current_quarter, [(event_fresh_pork_demand,'fresh_pork')])

        prime_beef_price = select_specific_entry('basedata_supplierquotes_table', 'selling_price', 'product', 'prime_beef')
        event_prime_beef_price = int(float(prime_beef_price)*0.9)
        update_data_in_table_column2('event_supplierquotes_table', 'selling_price', [(event_prime_beef_price,'prime_beef')])

        fresh_poultry_price = select_specific_entry('basedata_supplierquotes_table', 'selling_price', 'product', 'fresh_poultry')
        event_fresh_poultry_price = int(float(fresh_poultry_price)*0.9)
        update_data_in_table_column2('event_supplierquotes_table', 'selling_price', [(event_fresh_poultry_price,'fresh_poultry')])
                
        fresh_pork_price = select_specific_entry('basedata_supplierquotes_table', 'selling_price', 'product', 'fresh_pork')
        event_fresh_pork_price = int(float(fresh_pork_price)*0.9)
        update_data_in_table_column2('event_supplierquotes_table', 'selling_price', [(event_fresh_pork_price,'fresh_pork')])
                
        called_events.append(5)
    
            #PLAYER DATA MODIFICATION STRUCTURE NOT DETERMINED (THIS DOES IT ASSUMING THERE IS ONE PLAYER AND IT HAS ITS OWN TABLE)

    if event_roll == 6: 
        player_capital = select_specific_entry('basedata_player_data', 'value', 'data', 'capital')
        event_player_capital = int(float(player_capital) - 30000)
        update_data_in_table_column2('basedata_player_data', 'value', [(player_capital,'capital')])
        called_events.append(6)
    
    if event_roll == 7: 
        vegetable_greens_price = select_specific_entry('basedata_supplierquotes_table', 'selling_price', 'product', 'vegetable_greens')
        event_vegetable_greens_price = int(float(vegetable_greens_price)*1.25)
        update_data_in_table_column2('event_supplierquotes_table', 'selling_price', [(event_vegetable_greens_price,'vegetable_greens')])
                
        flour_price = select_specific_entry('basedata_supplierquotes_table', 'selling_price', 'product', 'flour')
        event_flour_price = int(float(flour_price)*1.25)
        update_data_in_table_column2('event_supplierquotes_table', 'selling_price', [(event_flour_price,'flour')])
        called_events.append(7)            
        
            

    if event_roll == 8:  #APPLIES IMMEDIATELY ONCE EVENT IS CALLED, NEED TO FIND A WAY TO DELAY BY ONE QUARTER AFTER NEWS RELEASE
        fresh_seafood_price = select_specific_entry('basedata_supplierquotes_table', 'selling_price', 'product', 'fresh_seafood')
        event_fresh_seafood_price = int(float(fresh_seafood_price)*1.3)
        update_data_in_table_column2('event_supplierquotes_table', 'selling_price', [(event_fresh_seafood_price,'fresh_seafood')])
                
        frozen_seafood_price = select_specific_entry('basedata_supplierquotes_table', 'selling_price', 'product', 'frozen_seafood')
        event_frozen_seafood_price = int(float(frozen_seafood_price)*1.3)
        update_data_in_table_column2('event_supplierquotes_table', 'selling_price', [(event_frozen_seafood_price,'frozen_seafood')])
        called_events.append(8)

    if event_roll == 9:         
        player_spirts_order = select_specific_entry('basedata_player_orders', 'product_order_quantity', 'product', 'spirits')
        if player_spirts_order > 500:
            event_player_spirts_order = int(500)
            update_data_in_table_column2('basedata_player_orders', 'product_order_quantity', [(event_player_spirts_order,'spirits')])
            called_events.append(9)
            
    if event_roll == 10:  
        tropical_greens_price = select_specific_entry('basedata_supplierquotes_table', 'selling_price', 'product', 'tropical_greens')
        event_tropical_greens_price = int(float(tropical_greens_price)*0.7)
        update_data_in_table_column2('event_supplierquotes_table', 'selling_price', [(event_tropical_greens_price,'tropical_greens')])
        called_events.append(10)
  
    if event_roll == 11:  #NEED MORE STRUCTURE TO DECIDE HOW TO INTRODUCE EVENTS BASED ON DAYS RATHER THAN QUARTERS
        called_events.append(11)

    if event_roll == 12:                         
        ice_cream_demand = select_specific_entry('basedata_demandforecast_table', current_quarter, 'product', 'ice_cream') #current_quarter takes the form e.g. q1_20x1
        event_ice_cream_demand = int(float(ice_cream_demand)*0.75)
        update_data_in_table_column2('event_demandforecast_table', current_quarter, [(event_ice_cream_demand,'ice_cream')])
        called_events.append(12)
        
    if event_roll == 13:                         
        chocolates_demand = select_specific_entry('basedata_demandforecast_table', current_quarter, 'product', 'chocolates') #current_quarter takes the form e.g. q1_20x1
        event_chocolates_demand = int(float(chocolates_demand)*1.3)
        update_data_in_table_column2('event_demandforecast_table', current_quarter, [(event_chocolates_demand,'chocolates')])
        called_events.append(13)
            
    if event_roll == 14:   
        update_table_column('basedata_demandforecast_table', current_quarter, 0.95, 'multiply')
        called_events.append(14)
        
    if event_roll == 15:   
        flour_demand = select_specific_entry('basedata_demandforecast_table', current_quarter, 'product', 'flour') #current_quarter takes the form e.g. q1_20x1
        event_flour_demand = int(float(flour_demand)*1.1)
        update_data_in_table_column2('event_demandforecast_table', current_quarter, [(event_flour_demand,'flour')])
        
        milk_demand = select_specific_entry('basedata_demandforecast_table', current_quarter, 'product', 'milk') #current_quarter takes the form e.g. q1_20x1
        event_milk_demand = int(float(milk_demand)*1.1)
        update_data_in_table_column2('event_demandforecast_table', current_quarter, [(event_milk_demand,'milk')])

        spices_demand = select_specific_entry('basedata_demandforecast_table', current_quarter, 'product', 'spices') #current_quarter takes the form e.g. q1_20x1
        event_spices_demand = int(float(spices_demand)*1.05)
        update_data_in_table_column2('event_demandforecast_table', current_quarter, [(event_spices_demand,'spices')])   
        called_events.append(15)
        
    if event_roll == 16:      
        frozen_poultry_whole_price = select_specific_entry('basedata_supplierquotes_table', 'selling_price', 'product', 'frozen_poultry_whole')
        event_frozen_poultry_whole_price = int(float(frozen_poultry_whole_price)*0.9)
        update_data_in_table_column2('event_supplierquotes_table', 'selling_price', [(event_frozen_poultry_whole_price,'frozen_poultry_whole')])
                
        fresh_poultry_parts_price = select_specific_entry('basedata_supplierquotes_table', 'selling_price', 'product', 'fresh_poultry_parts')
        event_fresh_poultry_parts_price = int(float(fresh_poultry_parts_price)*0.9)
        update_data_in_table_column2('event_supplierquotes_table', 'selling_price', [(event_fresh_poultry_parts_price,'fresh_poultry_parts')])
                
        called_events.append(16)
        
    if event_roll == 17:  
        canned_food_price = select_specific_entry('basedata_supplierquotes_table', 'selling_price', 'product', 'canned_food')
        event_canned_food_price = int(float(canned_food_price)*0.9)
        update_data_in_table_column2('event_supplierquotes_table', 'selling_price', [(event_canned_food_price,'canned_food')])
                
        snacks_and_chips_price = select_specific_entry('basedata_supplierquotes_table', 'selling_price', 'product', 'snacks_and_chips')
        event_snacks_and_chips_price = int(float(snacks_and_chips_price)*0.9)
        update_data_in_table_column2('event_supplierquotes_table', 'selling_price', [(event_snacks_and_chips_price,'snacks_and_chips')])
                
        sweets_price = select_specific_entry('basedata_supplierquotes_table', 'selling_price', 'product', 'sweets')
        event_sweets_price = int(float(sweets_price)*0.9)
        update_data_in_table_column2('event_supplierquotes_table', 'selling_price', [(event_sweets_price,'sweets')])
                   
        chocolates_price = select_specific_entry('basedata_supplierquotes_table', 'selling_price', 'product', 'chocolates')
        event_chocolates_price = int(float(chocolates_price)*0.9)
        update_data_in_table_column2('event_supplierquotes_table', 'selling_price', [(event_chocolates_price,'chocolates')])
        called_events.append(17)
        
    if event_roll == 18 and current_quarter == 3:  
        rice_price = select_specific_entry('basedata_supplierquotes_table', 'selling_price', 'product', 'rice')
        event_rice_price = int(float(rice_price)*1.25)
        update_data_in_table_column2('event_supplierquotes_table', 'selling_price', [(event_rice_price,'rice')])
        called_events.append(18)
        
        
    if event_roll == 19:          
        frozen_microwave_foods_demand = select_specific_entry('basedata_demandforecast_table', current_quarter, 'product', 'frozen_microwave_foods') #current_quarter takes the form e.g. q1_20x1
        event_frozen_microwave_foods_demand = int(float(frozen_microwave_foods_demand)*0.85)
        update_data_in_table_column2('event_demandforecast_table', current_quarter, [(event_frozen_microwave_foods_demand,'frozen_microwave_foods')])
        
        instant_noodles_demand = select_specific_entry('basedata_demandforecast_table', current_quarter, 'product', 'instant_noodles') #current_quarter takes the form e.g. q1_20x1
        event_instant_noodles_demand = int(float(instant_noodles_demand)*0.9)
        update_data_in_table_column2('event_demandforecast_table', current_quarter, [(event_instant_noodles_demand,'instant_noodles')])
        called_events.append(19)
        
    if event_roll == 20:                         
        frozen_pork_demand = select_specific_entry('basedata_demandforecast_table', current_quarter, 'product', 'frozen_pork') #current_quarter takes the form e.g. q1_20x1
        event_frozen_pork_demand = int(float(frozen_pork_demand)*0.95)
        update_data_in_table_column2('event_demandforecast_table', current_quarter, [(event_frozen_pork_demand,'frozen_pork')])
        
        fresh_pork_demand = select_specific_entry('basedata_demandforecast_table', current_quarter, 'product', 'fresh_pork') #current_quarter takes the form e.g. q1_20x1
        event_fresh_pork_demand = int(float(fresh_pork_demand)*0.95)
        update_data_in_table_column2('event_demandforecast_table', current_quarter, [(event_fresh_pork_demand,'fresh_pork')])
        called_events.append(20)
        
    return(event_roll) #event_roll to be stored in called_events list in main application


#revert_event is the event_roll you want to revert, e.g. 1
#this only applies to the supplier_quote table which is not built to factor in the entire span of time in the game (unlike the demandforecast)
def newsandevents_revert(current_quarter,revert_event):
    if revert_event == 1:
        frozen_pork_price = select_specific_entry('basedata_supplierquotes_table', 'selling_price', 'product', 'frozen_pork')
        event_frozen_pork_price = frozen_pork_price
        update_data_in_table_column2('event_supplierquotes_table', 'selling_price', [(event_frozen_pork_price,'frozen_pork')])
        
        frozen_pork_leadtime = select_specific_entry('basedata_supplierquotes_table', 'selling_price', 'product', 'frozen_pork')
        event_frozen_leadtime = frozen_pork_leadtime
        update_data_in_table_column2('event_supplierquotes_table', 'lead_time_express', [(event_frozen_leadtime,'frozen_pork')])

        fresh_pork_price = select_specific_entry('basedata_supplierquotes_table', 'selling_price', 'product', 'fresh_pork')
        event_fresh_pork_price = fresh_pork_price
        update_data_in_table_column2('event_supplierquotes_table', 'selling_price', [(event_fresh_pork_price,'fresh_pork')])
        
        fresh_pork_leadtime = select_specific_entry('basedata_supplierquotes_table', 'selling_price', 'product', 'fresh_pork')
        event_frozen_leadtime = fresh_pork_leadtime
        update_data_in_table_column2('event_supplierquotes_table', 'lead_time_express', [(event_frozen_leadtime,'fresh_pork')])
                                                                                            
    if revert_event == 2:                  
        print('Demand forecast based event. No reversion required. Reflect basedata_demandforecast_table when no event during quarter.')

    if revert_event == 3 and current_quarter == 4:                         
        wines_demand = select_specific_entry('basedata_demandforecast_table', current_quarter, 'product', 'wines') #current_quarter takes the form e.g. q1_20x1
        event_wines_demand = int(float(wines_demand)*1.2)
        update_data_in_table_column2('event_demandforecast_table', current_quarter, [(event_wines_demand,'wines')])

        spirits_demand = select_specific_entry('basedata_demandforecast_table', current_quarter, 'product', 'spirits') #current_quarter takes the form e.g. q1_20x1
        event_spirits_demand = int(float(spirits_demand)*1.2)
        update_data_in_table_column2('event_demandforecast_table', current_quarter, [(event_spirits_demand,'spirits')])
        
        beer_demand = select_specific_entry('basedata_demandforecast_table', current_quarter, 'product', 'beer') #current_quarter takes the form e.g. q1_20x1
        event_beer_demand = int(float(beer_demand)*1.2)
        update_data_in_table_column2('event_demandforecast_table', current_quarter, [(event_beer_demand,'beer')])

        prime_beef_demand = select_specific_entry('basedata_demandforecast_table', current_quarter, 'product', 'prime_beef') #current_quarter takes the form e.g. q1_20x1
        event_prime_beef_demand = int(float(prime_beef_demand)*1.2)
        update_data_in_table_column2('event_demandforecast_table', current_quarter, [(event_prime_beef_demand,'prime_beef')])

    
    if revert_event == 4:   
        update_table_column('event_supplierquotes_table', 'setup_costs_express', 0.833, 'multiply')
        
    if revert_event == 5:   
        prime_beef_demand = select_specific_entry('basedata_demandforecast_table', current_quarter, 'product', 'prime_beef') #current_quarter takes the form e.g. q1_20x1
        event_prime_beef_demand = int(float(prime_beef_demand)*0.769)
        update_data_in_table_column2('event_demandforecast_table', current_quarter, [(event_prime_beef_demand,'prime_beef')])

        fresh_poultry_parts_demand = select_specific_entry('basedata_demandforecast_table', current_quarter, 'product', 'fresh_poultry_parts') #current_quarter takes the form e.g. q1_20x1
        event_fresh_poultry_parts_demand = int(float(fresh_poultry_parts_demand)*0.87)
        update_data_in_table_column2('event_demandforecast_table', current_quarter, [(event_fresh_poultry_parts_demand,'fresh_poultry_parts')])

        fresh_pork_demand = select_specific_entry('basedata_demandforecast_table', current_quarter, 'product', 'fresh_pork') #current_quarter takes the form e.g. q1_20x1
        event_fresh_pork_demand = int(float(fresh_pork_demand)*0.87)
        update_data_in_table_column2('event_demandforecast_table', current_quarter, [(event_fresh_pork_demand,'fresh_pork')])

        prime_beef_price = select_specific_entry('basedata_supplierquotes_table', 'selling_price', 'product', 'prime_beef')
        event_prime_beef_price = int(float(prime_beef_price)*1.1)
        update_data_in_table_column2('event_supplierquotes_table', 'selling_price', [(event_prime_beef_price,'prime_beef')])

        fresh_poultry_price = select_specific_entry('basedata_supplierquotes_table', 'selling_price', 'product', 'fresh_poultry')
        event_fresh_poultry_price = int(float(fresh_poultry_price)*1.1)
        update_data_in_table_column2('event_supplierquotes_table', 'selling_price', [(event_fresh_poultry_price,'fresh_poultry')])
                
        fresh_pork_price = select_specific_entry('basedata_supplierquotes_table', 'selling_price', 'product', 'fresh_pork')
        event_fresh_pork_price = int(float(fresh_pork_price)*1.1)
        update_data_in_table_column2('event_supplierquotes_table', 'selling_price', [(event_fresh_pork_price,'fresh_pork')])
        
        
        #PLAYER DATA MODIFICATION STRUCTURE NOT DETERMINED (THIS DOES IT ASSUMING THERE IS ONE PLAYER AND IT HAS ITS OWN TABLE)
    if revert_event == 6: 
        player_capital = select_specific_entry('basedata_player_data', 'value', 'data', 'capital')
        event_player_capital = int(float(player_capital) + 30000)
        update_data_in_table_column2('basedata_player_data', 'value', [(player_capital,'capital')])
                        
    if revert_event == 7:                                 
        vegetable_greens_price = select_specific_entry('basedata_supplierquotes_table', 'selling_price', 'product', 'vegetable_greens')
        event_vegetable_greens_price = int(float(vegetable_greens_price)*(1/1.25))
        update_data_in_table_column2('event_supplierquotes_table', 'selling_price', [(event_vegetable_greens_price,'vegetable_greens')])
                
        flour_price = select_specific_entry('basedata_supplierquotes_table', 'selling_price', 'product', 'flour')
        event_flour_price = int(float(flour_price)*(1/1.25))
        update_data_in_table_column2('event_supplierquotes_table', 'selling_price', [(event_flour_price,'flour')])
                
        #APPLIES IMMEDIATELY ONCE EVENT IS CALLED, NEED TO FIND A WAY TO DELAY BY ONE QUARTER AFTER NEWS RELEASE
    if revert_event == 8:     
        fresh_seafood_price = select_specific_entry('basedata_supplierquotes_table', 'selling_price', 'product', 'fresh_seafood')
        event_fresh_seafood_price = int(float(fresh_seafood_price)*(1/1.3))
        update_data_in_table_column2('event_supplierquotes_table', 'selling_price', [(event_fresh_seafood_price,'fresh_seafood')])
                
        frozen_seafood_price = select_specific_entry('basedata_supplierquotes_table', 'selling_price', 'product', 'frozen_seafood')
        event_frozen_seafood_price = int(float(frozen_seafood_price)*(1/1.3))
        update_data_in_table_column2('event_supplierquotes_table', 'selling_price', [(event_frozen_seafood_price,'frozen_seafood')])
                
    if revert_event == 9: 
        print('NO CHANGE REQUIRED, JUST LET USER ORDERS OVERWRITE NUMBER OF ORDERS')
        
    if revert_event == 10: 
        tropical_greens_price = select_specific_entry('basedata_supplierquotes_table', 'selling_price', 'product', 'tropical_greens')
        event_tropical_greens_price = int(float(tropical_greens_price)*(1/0.7))
        update_data_in_table_column2('event_supplierquotes_table', 'selling_price', [(event_tropical_greens_price,'tropical_greens')])
    
    if revert_event == 11: 
        print('EVENT 11 TRIGGERED, CURRENTLY INACTIVE')
                                                             
    if revert_event == 12:
        ice_cream_demand = select_specific_entry('basedata_demandforecast_table', current_quarter, 'product', 'ice_cream') #current_quarter takes the form e.g. q1_20x1
        event_ice_cream_demand = int(float(ice_cream_demand)*(1/0.75))
        update_data_in_table_column2('event_demandforecast_table', current_quarter, [(event_ice_cream_demand,'ice_cream')])

    if revert_event == 13:
        chocolates_demand = select_specific_entry('basedata_demandforecast_table', current_quarter, 'product', 'chocolates') #current_quarter takes the form e.g. q1_20x1
        event_chocolates_demand = int(float(chocolates_demand)*(1/1.3))
        update_data_in_table_column2('event_demandforecast_table', current_quarter, [(event_chocolates_demand,'chocolates')])
    
    if revert_event == 14:
        update_table_column('basedata_demandforecast_table', current_quarter, (1/0.95), 'multiply')
   
    if revert_event == 15:
        flour_demand = select_specific_entry('basedata_demandforecast_table', current_quarter, 'product', 'flour') #current_quarter takes the form e.g. q1_20x1
        event_flour_demand = int(float(flour_demand)*(1/1.1))
        update_data_in_table_column2('event_demandforecast_table', current_quarter, [(event_flour_demand,'flour')])
        
        milk_demand = select_specific_entry('basedata_demandforecast_table', current_quarter, 'product', 'milk') #current_quarter takes the form e.g. q1_20x1
        event_milk_demand = int(float(milk_demand)*(1/1.1))
        update_data_in_table_column2('event_demandforecast_table', current_quarter, [(event_milk_demand,'milk')])

        spices_demand = select_specific_entry('basedata_demandforecast_table', current_quarter, 'product', 'spices') #current_quarter takes the form e.g. q1_20x1
        event_spices_demand = int(float(spices_demand)*(1/1.05))
        update_data_in_table_column2('event_demandforecast_table', current_quarter, [(event_spices_demand,'spices')])

    if revert_event == 16:
        frozen_poultry_whole_demand = select_specific_entry('basedata_demandforecast_table', current_quarter, 'product', 'frozen_poultry_whole') #current_quarter takes the form e.g. q1_20x1
        event_frozen_poultry_whole_demand = int(float(frozen_poultry_whole_demand)*1.25)
        update_data_in_table_column2('event_demandforecast_table', current_quarter, [(event_frozen_poultry_whole_demand,'frozen_poultry_whole')])
        
        fresh_poultry_parts_demand = select_specific_entry('basedata_demandforecast_table', current_quarter, 'product', 'fresh_poultry_parts') #current_quarter takes the form e.g. q1_20x1
        event_fresh_poultry_parts_demand = int(float(fresh_poultry_parts_demand)*1.25)
        update_data_in_table_column2('event_demandforecast_table', current_quarter, [(event_fresh_poultry_parts_demand,'fresh_poultry_parts')])
   
    if revert_event == 17:
        canned_food_price = select_specific_entry('basedata_supplierquotes_table', 'selling_price', 'product', 'canned_food')
        event_canned_food_price = int(float(canned_food_price)*1.1)
        update_data_in_table_column2('event_supplierquotes_table', 'selling_price', [(event_canned_food_price,'canned_food')])
                
        snacks_and_chips_price = select_specific_entry('basedata_supplierquotes_table', 'selling_price', 'product', 'snacks_and_chips')
        event_snacks_and_chips_price = int(float(snacks_and_chips_price)*1.1)
        update_data_in_table_column2('event_supplierquotes_table', 'selling_price', [(event_snacks_and_chips_price,'snacks_and_chips')])
                
        sweets_price = select_specific_entry('basedata_supplierquotes_table', 'selling_price', 'product', 'sweets')
        event_sweets_price = int(float(sweets_price)*1.1)
        update_data_in_table_column2('event_supplierquotes_table', 'selling_price', [(event_sweets_price,'sweets')])
                   
        chocolates_price = select_specific_entry('basedata_supplierquotes_table', 'selling_price', 'product', 'chocolates')
        event_chocolates_price = int(float(chocolates_price)*1.1)
        update_data_in_table_column2('event_supplierquotes_table', 'selling_price', [(event_chocolates_price,'chocolates')])
    
    if revert_event == 18:          
        rice_price = select_specific_entry('basedata_supplierquotes_table', 'selling_price', 'product', 'rice')
        event_rice_price = int(float(rice_price)*(1/1.25))
        update_data_in_table_column2('event_supplierquotes_table', 'selling_price', [(event_rice_price,'rice')])
                
    if revert_event == 19:  
        frozen_microwave_foods_demand = select_specific_entry('basedata_demandforecast_table', current_quarter, 'product', 'frozen_microwave_foods') #current_quarter takes the form e.g. q1_20x1
        event_frozen_microwave_foods_demand = int(float(frozen_microwave_foods_demand)*(1/0.85))
        update_data_in_table_column2('event_demandforecast_table', current_quarter, [(event_frozen_microwave_foods_demand,'frozen_microwave_foods')])
        
        instant_noodles_demand = select_specific_entry('basedata_demandforecast_table', current_quarter, 'product', 'instant_noodles') #current_quarter takes the form e.g. q1_20x1
        event_instant_noodles_demand = int(float(instant_noodles_demand)*(1/0.9))
        update_data_in_table_column2('event_demandforecast_table', current_quarter, [(event_instant_noodles_demand,'instant_noodles')])
    
    if revert_event == 20: 
        frozen_pork_demand = select_specific_entry('basedata_demandforecast_table', current_quarter, 'product', 'frozen_pork') #current_quarter takes the form e.g. q1_20x1
        event_frozen_pork_demand = int(float(frozen_pork_demand)*(1/0.95))
        update_data_in_table_column2('event_demandforecast_table', current_quarter, [(event_frozen_pork_demand,'frozen_pork')])
        
        fresh_pork_demand = select_specific_entry('basedata_demandforecast_table', current_quarter, 'product', 'fresh_pork') #current_quarter takes the form e.g. q1_20x1
        event_fresh_pork_demand = int(float(fresh_pork_demand)*(1/0.95))
        update_data_in_table_column2('event_demandforecast_table', current_quarter, [(event_fresh_pork_demand,'fresh_pork')])

#insert data into specific column of table based on index
def insert_new_row_into_table(table_name,input_data): #input data must match number of columns
    connection = connect_to_database()
    cursor = connection.cursor()
    postgreSQL_select_Query = "INSERT INTO {} ".format(table_name)
    postgreSQL_select_Query += " VALUES " #input data in the form[value1, value2...valuen]
    postgreSQL_select_Query += str(input_data) #string should look like: "(%s,%s)"
    cursor.execute(postgreSQL_select_Query)
    connection.commit()
    connection.close()

def drop_table(table_name): #input data must match number of columns
    connection = connect_to_database()
    cursor = connection.cursor()
    postgreSQL_select_Query = "DROP TABLE {} ".format(table_name)
    cursor.execute(postgreSQL_select_Query)
    connection.commit()
    connection.close()
    
### TEST CASES ###

# add_df_to_db("demand_forecast.csv")

# add_df_to_db2('basedata_demandforecast.xlsx', r'C:\Users\chinjooern\Desktop\Supermarket Game API')

# add_df_to_db2("basedata_supplierquotes.xlsx")

# clone_table_in_db('demand_forecast_table','cloned_demand_forecast_table2')

# clone_table_in_db('supplier_quotes_table','supplier_quotes_table3')

# select_table_columns('demand_forecast_table', ['q4_2003'])

# update_table_column('supplier_quotes_table', 'holding_cost', 2, 'multiply')
    
# select_table_columns('supplier_quotes_table', ['holding_cost'])
    
# render_table_from_database('basedata_player_table')

# render_table_from_database('basedata_demandforecast_table')

# select_table_columns('demand_forecast_table', ['q4_2003'], connection)

# add_own_table_columns('supplier_quotes_table', 'holding_cost2', 'holding_cost3')

# add_other_table_columns('supplier_quotes_table', 'supplier_quotes_table3', 'holding_cost', 'cloned_holding_cost')

# check_database_tables()

# get_columns_names('demand_forecast_table')
    
# get_columns_names('supplier_quotes_table')
    
# DEMAND_FORECAST = pd.read_csv("demand_forecast.csv") #strictly lower-case naming

# TABLE_NAME = 'demand_forecast_table' #strictly lower-case to prevent relationship errors when calling on the tables with SQL

# add_all_df_to_db(r'C:\Users\jooer\OneDrive\Desktop\Arthur Supermarket Code')

# insert_data_into_table_column('supplier_quotes_table', 'holding_cost3', [(1,999),(2,999),(3,999)])

# update_data_in_table_column('supplier_quotes_table', 'holding_cost3', [(999,4),(999,5),(999,6)]) #value followed by index

# update_data_in_table_column2('basedata_player_table', 'product_order_quantity', [(999,'milk'),(999,'prime_beef'),(999,'wines')]) #value followed by product

# randomize_demand_forecast('basedata_demandforecast2_table')

# select_specific_entry('basedata_supplierquotes_table', 'selling_price', 'product', 'rice')

# drop_table('basedata_player_table')

insert_new_row_into_table('basedata_player_table',(1,'milk','arthur',999,0,10,10,5,666,1,1,'2020-12-25'))
render_table_from_database('basedata_player_table')

