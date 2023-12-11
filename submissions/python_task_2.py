import pandas as pd
import os

def get_exhaustive_values(df):
    #Swap values and retain distance between points to get exhaustive list
    temp_df = df.copy()
    temp_df.id_start = df.id_end
    temp_df.id_end = df.id_start
    df = pd.concat([temp_df,df])
    
    return df


def get_mapping_distance_matrix(df):
    mapping_distance_matrix = dict()
    for i in df.values:
        mapping_distance_matrix[int(i[0])] = {}

    for i in df.values:
        mapping_distance_matrix[int(i[0])][int(i[1])] = i[2]
        
    return mapping_distance_matrix



def calculate_distance(start, end, dist_sum, mapping_distance_matrix):
    
    if start == end: 
        return 0
            
    if mapping_distance_matrix.get(start).get(end) != None:
        return mapping_distance_matrix[start][end]
    
    if mapping_distance_matrix.get(end).get(start) != None:
        return mapping_distance_matrix[end][start]
    
    if mapping_distance_matrix.get(start) == None:
        return 0
    
    for next_dist in mapping_distance_matrix.get(start).keys(): 
        if next_dist==end:
            return dist_sum + mapping_distance_matrix[start][next_dist]
        
        elif next_dist>start:
            dist_sum += mapping_distance_matrix[start][next_dist] + calculate_distance(next_dist, end, dist_sum, mapping_distance_matrix)
            return dist_sum
        
    return dist_sum



def calculate_distance_matrix(df)->pd.DataFrame():
    """
    Calculate a distance matrix based on the dataframe, df.

    Args:
        df (pandas.DataFrame)

    Returns:
        pandas.DataFrame: Distance matrix
    """
    df = get_exhaustive_values(df)
    mapping_distance_matrix = get_mapping_distance_matrix(df)
    
    startpoints = mapping_distance_matrix.keys()
    endpoints = [i for k,v in mapping_distance_matrix.items() for i in v]
    
    for start in startpoints:
        for end in endpoints:
            mapping_distance_matrix[start][end] = calculate_distance(start, end, 0, mapping_distance_matrix)
        
    emt_lis = [[k,i,j] for k,v in mapping_distance_matrix.items() for i,j in v.items()]
    dist_df = pd.DataFrame(emt_lis, columns = df.columns)

    df = dist_df.pivot_table(values='distance', index='id_start', columns='id_end', aggfunc='sum',  fill_value=0)

    return df



def unroll_distance_matrix(df)->pd.DataFrame():
    """
    Unroll a distance matrix to a DataFrame in the style of the initial dataset.

    Args:
        df (pandas.DataFrame)

    Returns:
        pandas.DataFrame: Unrolled DataFrame containing columns 'id_start', 'id_end', and 'distance'.
    """
    df = df.reset_index().melt(id_vars='id_start', var_name='id_end', value_name='distance')
    df = df[df.id_start != df.id_end]
    return df


def calculate_toll_rate(df)->pd.DataFrame():
    """
    Calculate toll rates for each vehicle type based on the unrolled DataFrame.

    Args:
        df (pandas.DataFrame)

    Returns:
        pandas.DataFrame
    """
    cost_maps = {'moto': 0.8 , 'rv': 1.5 , 'truck':2.2 , 'car': 1.2 , 'bus':3.6}
    
    for k,v in cost_maps.items():
        df[k] = df.distance * v

    return df


def create_time_mapping_matrix():
    time_mapping_mat = {'start_day': ['Monday', 'Tuesday', 'Wednesday', 'Saturday'],
              'end_day': ['Friday', 'Saturday', ' Sunday', 'Sunday'],
              'start_time': ['00:00:00', '10:00:00', '18:00:00', '00:00:00'],
              'end_time': ['10:00:00', '18:00:00', '23:59:59', '23:59:59']}

    time_mapping_mat = pd.DataFrame(time_mapping_mat)
    time_mapping_mat['start_time'] = pd.to_datetime(time_mapping_mat['start_time'], format='%H:%M:%S').dt.time
    time_mapping_mat['end_time'] = pd.to_datetime(time_mapping_mat['end_time'], format='%H:%M:%S').dt.time
    
    return time_mapping_mat



def merge_df(time_mapping_mat, df):
    time_mapping_mat['key'] = 1
    df['key'] = 1
    df = pd.merge(time_mapping_mat, df, on='key').drop('key', axis=1)
    
    return df


def calculate_time_based_toll_rates(df)->pd.DataFrame():
    """
    Calculate time-based toll rates for different time intervals within a day.

    Args:
        df (pandas.DataFrame)

    Returns:
        pandas.DataFrame
    """
    df = calculate_toll_rate(df)
    time_mapping_mat = create_time_mapping_matrix()
    df = merge_df(time_mapping_mat, df)
    
    columns_to_update = ['moto', 'rv', 'truck', 'car', 'bus']
    target_time1 = pd.to_datetime('00:00:00', format='%H:%M:%S').time()
    target_time2 = pd.to_datetime('10:00:00', format='%H:%M:%S').time()
    target_time3 = pd.to_datetime('18:00:00', format='%H:%M:%S').time()
    target_time4 = pd.to_datetime('23:59:59', format='%H:%M:%S').time()
    weekend_cdn = df['start_day'] != 'Saturday'

    condition = df['start_day'] == 'Saturday'
    df.loc[condition, columns_to_update] -= 0.7

    condition1 = df['start_time'] == target_time1
    condition2 = df['end_time'] == target_time2
    df.loc[condition1 & condition2 & weekend_cdn, columns_to_update] -= 0.8

    condition1 = df['start_time'] == target_time2
    condition2 = df['end_time'] == target_time3
    df.loc[condition1 & condition2 & weekend_cdn, columns_to_update] -= 1.2

    condition1 = df['start_time'] == target_time3
    condition2 = df['end_time'] == target_time4
    df.loc[condition1 & condition2 & weekend_cdn, columns_to_update] -= 0.8

    return df


def find_ids_within_ten_percentage_threshold(df, reference_id)->pd.DataFrame():
    """
    Find all IDs whose average distance lies within 10% of the average distance of the reference ID.

    Args:
        df (pandas.DataFrame)
        reference_id (int)

    Returns:
        pandas.DataFrame: DataFrame with IDs whose average distance is within the specified percentage threshold
                          of the reference ID's average distance.
    """
    perct=0.1
    avg_distance = df[df['id_start'] == reference_id]['distance'].mean()
    lower_bound = avg_distance - (avg_distance * perct)
    upper_bound = avg_distance + (avg_distance * perct)
    df = df[(df['distance'] >= lower_bound) & (df['distance'] <= upper_bound)]

    return df

# os.chdir(r'./datasets/')
# df = pd.read_csv(r'dataset-3.csv')
# c = calculate_distance_matrix(df)
# d = unroll_distance_matrix(c)
# t = find_ids_within_ten_percentage_threshold(d,1001402)
# e = calculate_toll_rate(d)
# calculate_time_based_toll_rates(t)
