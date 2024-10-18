import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import gmean, hmean, skew, kurtosis

# GUI class
class StatsApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Descriptive Statistics Analysis Tool")

        # File upload section
        self.label = tk.Label(root, text="Upload Excel File for Analysis", font=("Arial", 12))
        self.label.pack(pady=10)

        self.upload_button = tk.Button(root, text="Load Excel File", command=self.load_file)
        self.upload_button.pack(pady=10)

        # Dropdown to select columns
        self.column_dropdown = ttk.Combobox(root, values=[], state="readonly")
        self.column_dropdown.set("Select Column")
        self.column_dropdown.pack(pady=10)

        # Dropdown for main statistical category (Central Tendency, Dispersion, Visualization)
        self.stat_category = ttk.Combobox(root, values=["Central Tendency", "Dispersion", "Graphical Analysis"], state="readonly")
        self.stat_category.set("Select Statistical Category")
        self.stat_category.pack(pady=10)

        # Dropdown for specific technique (mean, median, mode, etc.)
        self.stat_technique = ttk.Combobox(root, values=[], state="readonly")
        self.stat_technique.set("Select Statistical Technique")
        self.stat_technique.pack(pady=10)

        # Dropdown for sub-techniques (arithmetic, geometric, etc.)
        self.sub_technique = ttk.Combobox(root, values=[], state="readonly")
        self.sub_technique.set("Select Sub-technique")
        self.sub_technique.pack(pady=10)

        self.analyze_button = tk.Button(root, text="Analyze", command=self.analyze_data)
        self.analyze_button.pack(pady=10)

        self.df = None

        # Binding dropdowns for dynamic updates
        self.stat_category.bind("<<ComboboxSelected>>", self.update_technique_options)
        self.stat_technique.bind("<<ComboboxSelected>>", self.update_sub_technique_options)

    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
        if file_path:
            try:
                self.df = pd.read_excel(file_path)
                self.column_dropdown['values'] = self.df.columns.tolist()
                messagebox.showinfo("File Loaded", "Excel file loaded successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {e}")
        else:
            messagebox.showwarning("File Not Found", "Please select a valid Excel file.")

    def update_technique_options(self, event):
        category = self.stat_category.get()
        if category == "Central Tendency":
            self.stat_technique['values'] = ["Mean", "Median", "Mode"]
        elif category == "Dispersion":
            self.stat_technique['values'] = ["Range", "Variance", "Standard Deviation", "Skewness", "Kurtosis"]
        elif category == "Graphical Analysis":
            self.stat_technique['values'] = ["Histogram", "Box Plot", "Normal Distribution"]

    def update_sub_technique_options(self, event):
        technique = self.stat_technique.get()
        if technique == "Mean":
            self.sub_technique['values'] = ["Arithmetic Mean", "Geometric Mean", "Harmonic Mean", "Weighted Mean"]
        else:
            self.sub_technique['values'] = []  # No sub-options for other techniques

    def analyze_data(self):
        if self.df is None:
            messagebox.showwarning("No Data", "Please load an Excel file first.")
            return

        col = self.column_dropdown.get()
        if col not in self.df.columns:
            messagebox.showerror("Error", f"Column '{col}' not found in the dataset.")
            return

        data = self.df[col].dropna()

        selected_category = self.stat_category.get()
        selected_technique = self.stat_technique.get()
        selected_sub_technique = self.sub_technique.get()

        if selected_category == "Central Tendency":
            result = None
            if selected_technique == "Mean":
                result = self.calculate_mean(data, selected_sub_technique)
            elif selected_technique == "Median":
                result = self.calculate_median(data)
            elif selected_technique == "Mode":
                result = self.calculate_mode(data)
            
            interpretation = self.interpret_result(result, selected_technique, selected_sub_technique)
            messagebox.showinfo("Result", f"Result: {result}\n\nInterpretation: {interpretation}")
        
        elif selected_category == "Dispersion":
            result = self.calculate_dispersion(data, selected_technique)
            interpretation = self.interpret_result(result, selected_technique)
            messagebox.showinfo("Result", f"Result: {result}\n\nInterpretation: {interpretation}")
        
        elif selected_category == "Graphical Analysis":
            if selected_technique == "Histogram":
                interpretation = self.interpret_plot("Histogram")
                messagebox.showinfo("Plot Interpretation", interpretation)
                self.plot_histogram(data)
            elif selected_technique == "Box Plot":
                interpretation = self.interpret_plot("Box Plot")
                messagebox.showinfo("Plot Interpretation", interpretation)
                self.plot_boxplot(data)
            elif selected_technique == "Normal Distribution":
                interpretation = self.interpret_plot("Normal Distribution")
                messagebox.showinfo("Plot Interpretation", interpretation)
                self.plot_normal_distribution(data)

    def calculate_mean(self, data, mean_type):
        if mean_type == "Arithmetic Mean":
            return data.mean()
        elif mean_type == "Geometric Mean":
            return gmean(data)
        elif mean_type == "Harmonic Mean":
            return hmean(data)
        elif mean_type == "Weighted Mean":
            weights = [1] * len(data)  # Placeholder for weights
            return sum(data * weights) / sum(weights)

    def calculate_median(self, data):
        return data.median()

    def calculate_mode(self, data):
        return data.mode().iloc[0] if not data.mode().empty else "No mode"

    def calculate_dispersion(self, data, technique):
        if technique == "Range":
            return data.max() - data.min()
        elif technique == "Variance":
            return data.var()
        elif technique == "Standard Deviation":
            return data.std()
        elif technique == "Skewness":
            return skew(data)
        elif technique == "Kurtosis":
            return kurtosis(data)

    def interpret_result(self, result, technique, sub_technique=None):
        if technique == "Mean":
            if sub_technique == "Arithmetic Mean":
                return f"The arithmetic mean is {result:.2f}. It reflects the average value in the dataset."
            elif sub_technique == "Geometric Mean":
                return f"The geometric mean is {result:.2f}. It’s useful for understanding multiplicative effects in the data."
            elif sub_technique == "Harmonic Mean":
                return f"The harmonic mean is {result:.2f}. This is ideal for rates and ratios."
            elif sub_technique == "Weighted Mean":
                return f"The weighted mean is {result:.2f}, accounting for different levels of importance of the values."
        elif technique == "Median":
            return f"The median is {result}. It divides the dataset into two equal halves, and it’s robust against outliers."
        elif technique == "Mode":
            return f"The mode is {result}. It represents the most frequent value in the dataset."
        elif technique == "Range":
            return f"The range is {result}. It shows the spread between the largest and smallest values."
        elif technique == "Variance":
            return f"The variance is {result:.2f}. It reflects how spread out the data is around the mean."
        elif technique == "Standard Deviation":
            return f"The standard deviation is {result:.2f}. It indicates how much variability there is in the dataset."
        elif technique == "Skewness":
            return f"The skewness is {result:.2f}. It measures the asymmetry of the data distribution. Positive values indicate a right skew, while negative values indicate a left skew."
        elif technique == "Kurtosis":
            return f"The kurtosis is {result:.2f}. It indicates the 'tailedness' of the data distribution. Higher values suggest heavier tails and more outliers."

    def interpret_plot(self, plot_type):
        if plot_type == "Histogram":
            return ("The histogram shows the frequency distribution of your data. It helps to visualize the shape of the data distribution. "
                    "If the data is normally distributed, you will see a bell curve. Look out for skewness, which can indicate the presence "
                    "of outliers or asymmetry in the data.")
        elif plot_type == "Box Plot":
            return ("The box plot displays the distribution of your data and highlights potential outliers. "
                    "The length of the box represents the interquartile range (IQR), and the line inside the box shows the median. "
                    "Outliers are plotted as individual points. If the box is skewed or if there are many outliers, this suggests asymmetry or the presence of extreme values.")
        elif plot_type == "Normal Distribution":
            return ("The normal distribution plot visualizes whether your data follows a normal distribution. "
                    "If the curve is symmetric and bell-shaped, your data is normally distributed. Deviations from this shape suggest "
                    "skewness or kurtosis, which can influence statistical analysis.")

    def plot_histogram(self, data):
        sns.histplot(data, kde=True)
        plt.title("Histogram")
        plt.show()

    def plot_boxplot(self, data):
        sns.boxplot(data=data)
        plt.title("Box Plot")
        plt.show()

    def plot_normal_distribution(self, data):
        sns.histplot(data, kde=True)
        plt.title("Normal Distribution")
        plt.show()

# Main GUI loop
if __name__ == "__main__":
    root = tk.Tk()
    app = StatsApp(root)
    root.mainloop()
