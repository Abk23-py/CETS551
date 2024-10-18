import pandas as pd
import matplotlib.pyplot as plt
import glob
from tqdm import tqdm
import seaborn as sns
from scipy import stats

# Folder Path on Google Drive
folder_path = folder_path = "C:\\Users\\DELL\\Desktop\\other files\\Project\\trip_data-20241014T032701Z-001\\trip_data"

# Get all CSV files in the folder
csv_files = glob.glob(folder_path + "*.csv")

# Initialize an empty list to store dataframes
dfs = []

# Loop over each file with tqdm progress bar, load it, rename columns, and append to the list
for file in tqdm(csv_files, desc="Loading and Processing CSV Files"):
    df = pd.read_csv(file)
    # Rename the columns
    df = df.rename(columns={
        "member_casual": "rider_type",
        "rideable_type": "bike_type"
    })
    # Append to the list of dataframes
    dfs.append(df)

# Combine all dataframes into one
combined_df = pd.concat(dfs, ignore_index=True)

# Sort the combined DataFrame by "started_at" column
combined_df = combined_df.sort_values(by="started_at").reset_index(drop=True)

combined_df.shape

# Missing values
missing_values = combined_df.isnull().sum()
missing_values

# Remove rows with any missing values
combined_df = combined_df.dropna()

combined_df.head()

# Most/least popular stations
combined_df["start_station_name"].value_counts()

def validate_station_mappings(dataframe):
    """
    Validate Station Name-to-ID mappings for both start and end stations.

    This function checks for inconsistencies between station names and station IDs by identifying
    cases where a station name is associated with multiple station IDs or where a station ID is
    associated with multiple station names. The results are printed to the console.

    Parameters:
        dataframe (pd.DataFrame): The DataFrame containing bike trip data with station names and IDs.
    """

    # Create dictionaries to map start station names to IDs and start station IDs to names
    start_name_to_ids = dataframe.groupby("start_station_name")["start_station_id"].unique().to_dict()
    start_id_to_names = dataframe.groupby("start_station_id")["start_station_name"].unique().to_dict()

    # Create dictionaries to map end station names to IDs and end station IDs to names
    end_name_to_ids = dataframe.groupby("end_station_name")["end_station_id"].unique().to_dict()
    end_id_to_names = dataframe.groupby("end_station_id")["end_station_name"].unique().to_dict()

    # Check for mismatches in start stations (name to multiple IDs)
    print("Start Station Names Mapping to Multiple IDs:")
    if any(len(ids) > 1 for ids in start_name_to_ids.values()):
        for name, ids in start_name_to_ids.items():
            if len(ids) > 1:
                print(f"{name}: {list(ids)} (Instances: {len(ids)})")
    else:
        print("nil")

    # Check for mismatches in start stations (ID to multiple names)
    print("\nStart Station IDs Mapping to Multiple Names:")
    if any(len(names) > 1 for names in start_id_to_names.values()):
        for station_id, names in start_id_to_names.items():
            if len(names) > 1:
                print(f"{station_id}: {list(names)} (Instances: {len(names)})")
    else:
        print("nil")

    # Check for mismatches in end stations (name to multiple IDs)
    print("\nEnd Station Names Mapping to Multiple IDs:")
    if any(len(ids) > 1 for ids in end_name_to_ids.values()):
        for name, ids in end_name_to_ids.items():
            if len(ids) > 1:
                print(f"{name}: {list(ids)} (Instances: {len(ids)})")
    else:
        print("nil")

    # Check for mismatches in end stations (ID to multiple names)
    print("\nEnd Station IDs Mapping to Multiple Names:")
    if any(len(names) > 1 for names in end_id_to_names.values()):
        for station_id, names in end_id_to_names.items():
            if len(names) > 1:
                print(f"{station_id}: {list(names)} (Instances: {len(names)})")
    else:
        print("nil")

# Call the function with your DataFrame
validate_station_mappings(combined_df)

# Delete trips starting or ending at station ID "S32020" (this station does not exist)
start_S32020 = combined_df["start_station_id"].value_counts().get("S32020", 0)
end_S32020 = combined_df["end_station_id"].value_counts().get("S32020", 0)

S32020_mismatch = start_S32020 + end_S32020
print(f"{S32020_mismatch} of the trips start or end at station S32020.")

combined_df = combined_df[~((combined_df["start_station_id"] == "S32020") |
                            (combined_df["end_station_id"] == "S32020"))]

# Count instances of "A32046" under start and end station IDs for the name "Tremont St at Court St"
count_start = combined_df[(combined_df["start_station_id"] == "A32046") &
                          (combined_df["start_station_name"] == "Tremont St at Court St")].shape[0]

count_end = combined_df[(combined_df["end_station_id"] == "A32046") &
                        (combined_df["end_station_name"] == "Tremont St at Court St")].shape[0]

# Total instances
total_count = count_start + count_end
print(f"Total instances of station ID A32046 mismatched with Tremont St at Court St: {total_count}")

# Update start_station_name and end_station_name for "A32046" instances
# Station ID A32046 is for "Canal St at Causeway St" not "Tremont St at Court St"

combined_df.loc[(combined_df["start_station_id"] == "A32046") &
                (combined_df["start_station_name"] == "Tremont St at Court St"),
                "start_station_name"] = "Canal St at Causeway St"

combined_df.loc[(combined_df["end_station_id"] == "A32046") &
                (combined_df["end_station_name"] == "Tremont St at Court St"),
                "end_station_name"] = "Canal St at Causeway St"

def update_station_names(dataframe, old_name, new_name):
    """
    Update station names in both start and end station columns of the DataFrame.

    This function replaces occurrences of the specified old station name with the new station name
    in both "start_station_name" and "end_station_name" columns of the DataFrame.

    Parameters:
        dataframe (pd.DataFrame): The DataFrame containing bike trip data with station names.
        old_name (str): The old station name to be replaced.
        new_name (str): The new station name to replace with.
    """
    # Update both start and end station names
    dataframe.loc[dataframe["start_station_name"] == old_name, "start_station_name"] = new_name
    dataframe.loc[dataframe["end_station_name"] == old_name, "end_station_name"] = new_name

# List of changes to be made
changes = [
    ["Canal St. at Causeway St.", "Canal St at Causeway St"],
    ["Tremont St. at Court St.", "Tremont St at Court St"],
    ["Chestnut Hill Ave. at Ledgemere Road", "Chestnut Hill Ave at Ledgemere Rd"],
    ["Centre St. at Allandale St.", "Centre St at Allandale St"],
    ["Hyde Square - Barbara St at Centre St", "Hyde Square - Centre St at Perkins St"],
    ["Swan Pl. at Minuteman Bikeway", "Swan Place at Minuteman Bikeway"],
    ["CambridgeSide Galleria - CambridgeSide PL at Land Blvd", "Cambridgeside Pl at Land Blvd"],
    ["Summer St at Quincy St", "Somerville Hospital"],
    ["Everett Square (Broadway at Chelsea St)", "Everett Square (Broadway at Norwood St)"],
    ["Damrell st at Old Colony Ave", "Damrell St at Old Colony Ave"]
]

# Applying the changes to the DataFrame
for old_name, new_name in changes:
    update_station_names(combined_df, old_name, new_name)

# Confirmation message
print("Station names updated successfully.")

# Check for mismatch again
validate_station_mappings(combined_df)

"""
The \xa0 character is the Unicode representation for a non-breaking space (NBSP). This character
is different from a regular space ( " " , Unicode U+0020 ) although they appear the same.
"""

# Standardize station names for A32046
standard_name = "Canal St at Causeway St"

# Identify and replace the inconsistent names
combined_df.loc[
    (combined_df["end_station_id"] == "A32046") &
    (combined_df["end_station_name"].isin(["Canal St at Causeway St",
    "Canal St\xa0at\xa0Causeway\xa0St"])), "end_station_name"] = standard_name

# Final check for mismatch
validate_station_mappings(combined_df)

combined_df

combined_df.dtypes

# Check for date/time rows that contain fractional seconds
fractional_seconds = combined_df[combined_df["started_at"].str.contains(r"\.\d+")]
fractional_seconds[["started_at", "ended_at"]].head()

# Convert started_at and ended_at columns to datetime format
combined_df["started_at"] = pd.to_datetime(combined_df["started_at"], format="%Y-%m-%d %H:%M:%S", errors='coerce')
combined_df["ended_at"] = pd.to_datetime(combined_df["ended_at"], format="%Y-%m-%d %H:%M:%S", errors='coerce')

combined_df[["started_at", "ended_at"]].dtypes

# TOTAL TRIPS PER HOUR OF DAY

# Extract the hours the trips started
combined_df["start_hour"] = combined_df["started_at"].dt.hour

# Group by Hour of Day to calculate total trips
hourly_trip_starts = combined_df.groupby("start_hour").size().reset_index(name="Total Start Trips")

# Plotting
plt.figure(figsize=(12, 4))
plt.plot(hourly_trip_starts["start_hour"], hourly_trip_starts["Total Start Trips"], marker='o', color="blue")

# Set x-axis ticks to show every hour
plt.xticks(range(24))

# Show morning and evening peaks
plt.axvline(x=8, color='green', linestyle='--', label='Morning Peak Hour (08:00 A.M.)')
plt.axvline(x=17, color='red', linestyle='--', label='Evening Peak Hour (05:00 P.M.)')

# Add titles and labels
plt.title("Total Trips by Hour of Day")
plt.xlabel("Hour of Day")
plt.ylabel("Total Trips")

# Remove vertical grid lines
plt.grid(axis='y')

# Remove plot boundaries at right, left, and top
plt.gca().spines['top'].set_visible(False)
plt.gca().spines['right'].set_visible(False)
plt.gca().spines['left'].set_visible(False)

plt.legend()
plt.tight_layout()
plt.show()

# TOTAL TRIPS PER HOUR OF DAY AND DAY OF WEEK

# Extract the day of the week the trips started
combined_df["start_day_of_week"] = combined_df["started_at"].dt.day_name()

# Group by Day of the Week and Hour of Day to calculate total trips
hourly_weekly_trip_starts = combined_df.groupby(["start_day_of_week", "start_hour"]).size().unstack(fill_value=0)

# Reorder the days of the week for proper visualization
days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
hourly_weekly_trip_starts = hourly_weekly_trip_starts.reindex(days_order)

# Plotting
plt.figure(figsize=(12, 4))
for day in hourly_weekly_trip_starts.index:
    plt.plot(hourly_weekly_trip_starts.columns, hourly_weekly_trip_starts.loc[day], marker='o', label=day)

plt.xticks(range(24))
plt.title("Daily Trips by Hour of Day and Day of Week")
plt.xlabel("Hour of Day")
plt.ylabel("Total Trips")
plt.grid(axis='y')

# Remove plot boundaries at right, left, and top
plt.gca().spines['top'].set_visible(False)
plt.gca().spines['right'].set_visible(False)
plt.gca().spines['left'].set_visible(False)

plt.legend(title="Day of Week")
plt.tight_layout()
plt.show()

# TOTAL TRIPS PER HOUR OF DAY AND DAY OF WEEK (HEATMAP)

# Plotting the heatmap
plt.figure(figsize=(12, 4))
sns.heatmap(hourly_weekly_trip_starts, cmap="Blues", annot=False, cbar_kws={'label': 'Total Trips'},
            linewidths=0.5, linecolor='black', square=True)

# Customize the plot
plt.title("Daily Trips by Hour of Day and Day of Week", fontsize=16)
plt.xlabel("Hour of Day", fontsize=12)
plt.ylabel("Day of Week", fontsize=12)

# Set the x-ticks to show every hour
plt.xticks(ticks=range(24), labels=range(24))

# Remove plot boundaries at right, left, and top
plt.gca().spines['top'].set_visible(False)
plt.gca().spines['right'].set_visible(False)
plt.gca().spines['left'].set_visible(False)

plt.tight_layout()
plt.show()

# TOTAL TRIPS PER HOUR OF DAY BY RIDER TYPE

# Group by Hour of Day and Rider Type to calculate total trips
hourly_trip_starts_by_rider_type = combined_df.groupby(["start_hour", "rider_type"]).size().unstack(fill_value=0)

# Plotting
plt.figure(figsize=(12, 4))

# Plot separate lines for each rider type
for rider_type in hourly_trip_starts_by_rider_type.columns:
    plt.plot(hourly_trip_starts_by_rider_type.index, hourly_trip_starts_by_rider_type[rider_type],
             marker='o', label=rider_type.capitalize())

# Set x-axis ticks to show every hour
plt.xticks(range(24))

# Add titles and labels
plt.title("Total Trips by Hour of Day by Rider Type")
plt.xlabel("Hour of Day")
plt.ylabel("Total Trips")

# Remove vertical grid lines
plt.grid(axis='y')

# Remove plot boundaries at right, left, and top
plt.gca().spines['top'].set_visible(False)
plt.gca().spines['right'].set_visible(False)
plt.gca().spines['left'].set_visible(False)

plt.legend(title="Rider Type")
plt.tight_layout()
plt.show()

# RIDER TYPE ANALYSIS

rider_type_analysis = combined_df.groupby(['rider_type', 'bike_type']).size().unstack()
rider_type_analysis.plot(kind='bar', stacked=True)
plt.title("Rider Type Analysis by Bike Type")
plt.ylabel("Total Trips")
plt.xlabel("Rider Type")
plt.xticks(rotation=0)
plt.show()

# BOXPLOT FOR TRIP DURATION BY BIKE TYPE

plt.figure(figsize=(4, 12))
sns.boxplot(x='bike_type', y='trip_duration', data=combined_df)
plt.title("Trip Duration by Bike Type")
plt.show()

# TOTAL TRIPS PER HOUR OF DAY BY BIKE TYPE

# Group by Hour of Day and Bike Type to calculate total trips
hourly_trip_starts_by_bike_type = combined_df.groupby(["start_hour", "bike_type"]).size().unstack(fill_value=0)

# Plotting
plt.figure(figsize=(12, 4))

# Plot separate lines for each bike type
for bike_type in hourly_trip_starts_by_bike_type.columns:
    plt.plot(hourly_trip_starts_by_bike_type.index, hourly_trip_starts_by_bike_type[bike_type],
             marker='o', label=bike_type.replace("_", " ").capitalize())

# Set x-axis ticks to show every hour
plt.xticks(range(24))

# Add titles and labels
plt.title("Total Trips by Hour of Day by Bike Type")
plt.xlabel("Hour of Day")
plt.ylabel("Total Trips")

# Remove vertical grid lines
plt.grid(axis='y')

# Remove plot boundaries at right, left, and top
plt.gca().spines['top'].set_visible(False)
plt.gca().spines['right'].set_visible(False)
plt.gca().spines['left'].set_visible(False)

plt.legend(title="Bike Type")
plt.tight_layout()
plt.show()

# Create a new column for trip duration in seconds
combined_df["trip_duration"] = (combined_df["ended_at"] - combined_df["started_at"]).dt.total_seconds()

# Filter the trip durations for electric and classic bikes
electric_durations = combined_df[combined_df["bike_type"] == "electric_bike"]["trip_duration"]
classic_durations = combined_df[combined_df["bike_type"] == "classic_bike"]["trip_duration"]

# Perform independent t-test
t_stat, p_value = stats.ttest_ind(electric_durations, classic_durations)

# Output the result
print(f"T-statistic: {t_stat}, P-value: {p_value}")


