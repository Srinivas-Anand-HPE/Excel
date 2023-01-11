import pandas as pd


def excel_to_df(path, excel_sheet):
    df = pd.read_excel(path, sheet_name=excel_sheet)  # Store Excel Data in dataframe
    df.drop(range(0, 10), inplace=True)  # Drop the additional top rows
    columns_to_keep_main = range(1, 15)  # To which Columns to Keep
    df = df.iloc[:, columns_to_keep_main]
    df.dropna(how="all", inplace=True)  # Drop Null Valued Rows
    return df  # DataFrame


def rename_columns(df, columns_rename={'Report For:': 'Image', 'CSM V1.3.0-final': 'Count', 'Unnamed: 3': 'C & H',
                                       'Unnamed: 4': 'C', 'Unnamed: 5': 'H', 'Unnamed: 6': 'M', 'Unnamed: 7': 'L',
                                       'Unnamed: 8': 'No Fix', 'Unnamed: 9': 'Max', 'Unnamed: 10': 'Min',
                                       'Unnamed: 11': 'Total', 'Unnamed: 14': 'Chart', 'Unnamed: 12': 'Fixable C',
                                       'Unnamed: 13': 'Fixable H'}):
    df.rename(columns=columns_rename, inplace=True)
    df.rename(columns={df.columns[1]: 'Count'}, inplace=True)
    return df  # DataFrame


def save_sheet(df, writer, sheet_name):
    df.to_excel(writer, sheet_name=sheet_name)


def get_desired_rows(df, columns_to_keep=["C & H", "C", "H", "Chart", "Fixable C", "Fixable H"]):
    df = df[columns_to_keep]
    return df


def sort_keys(df, keys):
    df.sort_values(keys, ascending=False)
    return df  # DataFrame


def desired_output_1(path, sheet):
    return rename_columns(excel_to_df(path, sheet)).set_index("Image")


def desired_output_2(df, writer):
    df2 = get_desired_rows(df)
    df2 = df2[df2["C & H"] > 0].drop("C & H", axis='columns')
    df2 = sort_keys(df2, ["C", "H"])
    save_sheet(df2, writer, "Sorted Data C&H")

    df3 = get_desired_rows(df, ["C & H", "M", "L"])
    df3 = df3[(df3["C & H"]) == 0].drop("C & H", axis='columns')

    df4 = df3[(df3["M"] + df3["L"]) == 0]

    df3 = df3[(df3["M"] + df3["L"]) > 0]
    df3 = sort_keys(df3, ["M", "L"])
    save_sheet(df3, writer, "Sorted Data M&L")

    df4 = get_desired_rows(df4, [])
    save_sheet(df4, writer, "No Vulnerabilities")


def desired_output_3(df1, df2):
    df1 = df1.drop(['Chart'], axis=1)
    df2 = df2.drop(['Chart'], axis=1)
    df = df1.merge(df2, how="outer", on="Image", indicator=True).fillna(0)

    numeric_rows = ["Count", "C & H", "C", "H", "M", "L", "No Fix", "Max", "Min", "Total", "Fixable C", "Fixable H"]
    for i in numeric_rows:
        df[i] = df[i + "_x"] - df[i + "_y"]

    df['Status Changes'] = df['_merge']
    df.pop('_merge')
    df['Status Changes'] = df['Status Changes'].replace("both", "")
    df['Status Changes'] = df['Status Changes'].replace("left_only", "New")
    df['Status Changes'] = df['Status Changes'].replace("right_only", "Deleted")
    df['Summary_temp1'] = ""
    df['Summary_temp2'] = ""

    rows = df.shape[0]

    for i in range(rows):
        if (df["C_x"][i] != df["C_y"][i]) and (df["C_x"][i] != 0):
            df['Summary_temp1'][i] = "C changed from " + df["C_y"][i].astype(str) + " to " + df["C_x"][i].astype(
                str) + ","
        if (df["H_x"][i] != df["H_y"][i]) and (df["H_x"][i] != 0):
            df['Summary_temp2'][i] = "H changed from " + df["H_y"][i].astype(str) + " to " + df["H_x"][i].astype(str)

    df['Summary'] = df['Summary_temp1'] + df["Summary_temp2"]
    for i in numeric_rows:
        df.pop(i + "_x")
        df.pop(i + "_y")

    df.pop('Summary_temp1')
    df.pop('Summary_temp2')

    return df


if __name__ == '__main__':
    print("Hi")
    excel_writer = pd.ExcelWriter("Output.xlsx")
    path_current = "Snyk-Report-V1.4.0-beta.29-1-3-23.xlsm"
    sheet_current = "Summary"
    data1 = desired_output_1(path_current, sheet_current)
    desired_output_2(data1, excel_writer)
    save_sheet(data1, excel_writer, "Summary")
    path_previous = "Snyk-Report - V1.3.1-alpha.3-11-30-2022.xlsm"
    sheet_previous = "Summary"
    data2 = desired_output_1(path_previous, sheet_previous)
    save_sheet(data2, excel_writer, "Previous Summary")
    output = desired_output_3(data1, data2)
    save_sheet(output, excel_writer, "Changes")
    excel_writer.save()
    print("Done")
