import pandas as pd
import tkinter as tk
from tkinter import ttk, filedialog

class FeatureFilterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Digital Species Key 1.0.0")
        self.root.geometry("600x650")
        self.root.configure(bg="#ded1ad")

        self.df = None
        self.filtered_df = None
        self.applied_filters = []

        self.load_button = tk.Button(root, text="Load Excel File", command=self.load_file,
                             bg="#4a90e2", fg="white", font=("Arial", 10, "bold"))
        self.load_button.pack(pady=10)

        self.feature_combo = ttk.Combobox(root, state="readonly")
        self.feature_combo.bind("<<ComboboxSelected>>", self.update_value_options)

        self.value_combo = ttk.Combobox(root, state="readonly")

        self.filter_button = tk.Button(root, text="Apply Filter", command=self.apply_filter,
                               bg="#4a90e2", fg="white", font=("Arial", 10, "bold"))
        self.reset_button = tk.Button(root, text="Reset Filters", command=self.reset_filters,
                              bg="#888", fg="white", font=("Arial", 10, "bold"))

        self.result_label = tk.Label(root, text="Remaining entries: N/A", wraplength=500,
                             bg="#f0f0f5", fg="#333", font=("Arial", 10))
        self.result_label.pack(pady=5)

        self.filters_label = tk.Label(root, text="Filters: None", wraplength=500, justify="left",
                              bg="#f0f0f5", fg="#336699", font=("Arial", 10, "italic"))
        self.filters_label.pack(pady=5)

        self.listbox_frame = tk.Frame(root)
        self.listbox_scrollbar = tk.Scrollbar(self.listbox_frame, orient="vertical")
        self.species_listbox = tk.Listbox(self.listbox_frame, yscrollcommand=self.listbox_scrollbar.set,
                                  width=80, height=15, bg="white", fg="black", relief="sunken", borderwidth=2)
        self.listbox_scrollbar.config(command=self.species_listbox.yview)

        self.species_listbox.pack(side="left", fill="both", expand=True)
        self.listbox_scrollbar.pack(side="right", fill="y")
        self.listbox_frame.pack(pady=10)

        self.diff_features_label = tk.Label(root, text="Best features to narrow down further", wraplength=500)
        self.diff_features_label.pack(pady=5)

        self.diff_features_listbox = tk.Listbox(root, width=80, height=5)
        self.diff_features_listbox.pack(pady=5)

    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx *.xls")])
        if file_path:
            self.df = pd.read_excel(file_path)
            self.filtered_df = self.df.copy()
            self.applied_filters = []

            self.feature_combo["values"] = sorted([col for col in self.df.columns if col.lower() != "species"])
            self.feature_combo.set('')
            self.feature_combo.pack(pady=5)

            self.value_combo.set('')
            self.value_combo.pack(pady=5)

            self.filter_button.pack(pady=5)
            self.reset_button.pack(pady=5)

            self.result_label.config(text=f"Remaining entries: {len(self.filtered_df)}")
            self.update_filters_label()
            self.update_species_list()

            self.highlight_diff_features()

    def update_value_options(self, event):
        selected_feature = self.feature_combo.get()
        if selected_feature and self.filtered_df is not None:
            raw_values = self.filtered_df[selected_feature].dropna().astype(str).tolist()
            split_values = []

            for val in raw_values:
                split_values.extend([v.strip() for v in val.split(",")])

            unique_values = sorted(set(split_values), key=lambda x: (x.isdigit(), float(x) if x.replace('.', '', 1).isdigit() else x))

            self.value_combo["values"] = unique_values
            if unique_values:
                self.value_combo.current(0)

    def apply_filter(self):
        feature = self.feature_combo.get()
        value = self.value_combo.get()

        if feature and value:
            col_dtype = self.filtered_df[feature].dtype

            try:
                if pd.api.types.is_numeric_dtype(col_dtype):
                    value = float(value)
                    is_numeric = True
                else:
                    is_numeric = False
            except ValueError:
                is_numeric = False

            def match(row_val):
                if pd.isna(row_val):
                    return True
                if isinstance(row_val, str):
                    parts = [part.strip() for part in row_val.split(",")]
                    if is_numeric:
                        try:
                            parts = [float(p) for p in parts]
                            return value in parts
                        except ValueError:
                            return False
                    else:
                        return str(value) in parts
                if is_numeric:
                    return row_val == value
                return str(row_val) == str(value)

            self.filtered_df = self.filtered_df[
                self.filtered_df[feature].apply(match)
            ]

            self.applied_filters.append((feature, value))
            self.result_label.config(text=f"Remaining entries: {len(self.filtered_df)}")
            self.update_filters_label()
            self.update_species_list()
            self.highlight_diff_features()
    def reset_filters(self):
        if self.df is not None:
            self.filtered_df = self.df.copy()
            self.applied_filters = []
            self.feature_combo.set('')
            self.value_combo.set('')
            self.result_label.config(text=f"Remaining entries: {len(self.filtered_df)}")
            self.update_filters_label()
            self.update_species_list()

            self.highlight_diff_features()

    def update_filters_label(self):
        if self.applied_filters:
            text = "Filters: " + " | ".join(f"{f} = {v}" for f, v in self.applied_filters)
        else:
            text = "Filters: None"
        self.filters_label.config(text=text)

    def update_species_list(self):
        self.species_listbox.delete(0, tk.END)
        if "Species" in self.filtered_df.columns:
            for species in self.filtered_df["Species"]:
                self.species_listbox.insert(tk.END, species)
        else:
            for i, row in self.filtered_df.iterrows():
                self.species_listbox.insert(tk.END, f"Entry {i + 1}")

    def highlight_diff_features(self):
        self.diff_features_listbox.delete(0, tk.END)

        for feature in self.df.columns:
            if feature.lower() != "species":
                unique_values = self.filtered_df[feature].dropna().unique()
                if len(unique_values) > 1: 
                    self.diff_features_listbox.insert(tk.END, feature)

if __name__ == "__main__":
    root = tk.Tk()
    app = FeatureFilterApp(root)
    root.mainloop()