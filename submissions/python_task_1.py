import pandas as pd



def generate_car_matrix(df)->pd.DataFrame:
    """
    Creates a DataFrame  for id combinations.

    Args:
        df (pandas.DataFrame)

    Returns:
        pandas.DataFrame: Matrix generated with 'car' values, 
                          where 'id_1' and 'id_2' are used as indices and columns respectively.
    """
    df = df.pivot(index='id_1', columns='id_2', values='car')
    df.fillna('0',inplace=True)
    df=df.astype('float')
   
    return df



def get_type_count(df) -> dict:
    """
    Categorizes 'car' values into types and returns a dictionary of counts.

    Args:
        df (pandas.DataFrame)

    Returns:
        dict: A dictionary with car types as keys and their counts as values.
    """
    df['car_type'] = pd.cut(df['car'],
                            bins=[float('-inf'), 15, 25, float('inf')],
                            labels=['low', 'medium', 'high'],
                            right=False)

    type_counts = df['car_type'].value_counts().to_dict()
    df = dict(sorted(type_counts.items()))

    return df



def get_bus_indexes(df):
    """
    Identifies indices where 'bus' values are greater than twice the mean value.

    Args:
        df (pandas.DataFrame)

    Returns:
        list: A list of indices sorted in ascending order.
    """
    bus_mean = df['bus'].mean()
    df = df[df['bus'] > 2 * bus_mean].index.tolist()
    df.sort()

    return df



def filter_routes(df):
    """
    Returns a sorted list of values of column 'route' for which the average of 'truck' column is greater than 7.

    Args:
        df (pandas.DataFrame)

    Returns:
        list: A sorted list of 'route' values.
    """
    route_avg_truck = df.groupby('route')['truck'].mean()
    filtered_routes = route_avg_truck[route_avg_truck > 7].index.tolist()
    filtered_routes.sort()

    return filtered_routes


def multiply_matrix(input_df):
    """
    Modifies each value in the DataFrame based on specific logic.

    Args:
        input_df (pandas.DataFrame): The input DataFrame.

    Returns:
        pandas.DataFrame: The modified DataFrame with values rounded to 1 decimal place.
    """
    modified_df = input_df.copy()
    modified_df[matrix > 20] *= 0.75
    modified_df[matrix <= 20] *= 1.25
    modified_df = modified_df.round(1)

    return modified_df



def multiply_matrix(input_df):
    """
    Modifies each value in the DataFrame based on specified logic and returns the modified DataFrame.

    Args:
        input_df (pandas.DataFrame): Input DataFrame.

    Returns:
        pandas.DataFrame: Modified DataFrame.
    """
    modified_df = input_df.copy()  
    modified_df[input_df > 20] *= 0.75
    modified_df[input_df <= 20] *= 1.25
    modified_df = modified_df.round(1)

    return modified_df




def time_check(df)->pd.Series:
    """
    Use shared dataset-2 to verify the completeness of the data by checking whether the timestamps for each unique (`id`, `id_2`) pair cover a full 24-hour and 7 days period

    Args:
        df (pandas.DataFrame)

    Returns:
        pd.Series: return a boolean series
    """
    # Write your logic here

    raise NotImplementedError("This function is not implemented yet")

# df=pd.read_csv('dataset-1.csv')
# get_type_count(df)
# get_bus_indexes(df)
# filter_routes(df)
# c=generate_car_matrix(df)
# modified_result = multiply_matrix(c)






