import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

file="/Users/spanta/Documents/batch_aeneas_scripts/batch_directory/QC_data/BMQBSMN2DA_epo_eng_plot_cdf.csv"
data_req = pd.read_table(file, sep=",")
arr = data_req.values
arr.sort(axis=0)


data_req = pd.DataFrame(arr, index=data_req.index, columns=data_req.columns)

#sort values per column
sorted_values = data_req.apply(lambda x: x.sort_values())


fig, ax = plt.subplots()

for col in sorted_values.columns:

    y = np.linspace(0.,1., len(sorted_values[col].dropna()))
    ax.plot(sorted_values[col].dropna(), y,label=col)

legend = ax.legend(loc='lower right', shadow=True, fontsize='medium')



plt.xlim([0, 5])
filename=(file.split('/')[-1]).split('_')[0]
plt.savefig('/Users/spanta/Documents/batch_aeneas_scripts/batch_directory/QC_data/'+filename+'.png')
#plt.show()