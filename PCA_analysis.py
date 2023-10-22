from sklearn.decomposition import PCA
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
from bidi.algorithm import get_display
from arabic_reshaper import reshape
import matplotlib.ticker as mtick
import os


def process_data(info):
    data = pd.DataFrame.from_dict(info, orient='index', columns=['CREDIT', 'RENT', 'longitude', 'latitude','Meterage','District'])

    districts = set(data['District'])

    data['CREDIT'] /= 1000000
    data['RENT'] /= 1000000
    data['longitude'], data['latitude'] = data['longitude'].astype(float), data['latitude'].astype(float)
    mask_prices = (data['CREDIT'] < 100) | (data['CREDIT'] > 2000) | (data['RENT'] < 1) | (data['RENT'] > 100)
    data = data.loc[~mask_prices].dropna(subset=['CREDIT', 'RENT'])

    locs = data[['longitude', 'latitude']].dropna()
    mask_locs = (locs['latitude'] > 36) | (locs['latitude'] < 35.55) | (locs['longitude'] < 51.10) | (locs['longitude'] > 51.60)
    data_location = data.loc[~(mask_locs|mask_prices)].dropna()
    return data, data_location, districts


def compute_PCA_districts(files_path, treshhold):
    with open(files_path+"table.json" , encoding='utf-8') as f:
        info = json.load(f)
    data, data_location, districts = process_data(info=info)
    conversion_rates = {}

    for district in districts:
        data_district = data.loc[data['District'] == district]

        if len(data_district) > treshhold:
            pca = PCA()
            pca_fit = pca.fit_transform(data_district[['CREDIT', 'RENT']])

            conversion_rate = abs(pca.components_[0,1])

            # print(f'Conversion Rate of district {district}:\t {conversion_rate*100 :.2f}%')
            conversion_rates[district] = conversion_rate

    fig = plt.figure(figsize=(20, 8))
    
    PCA_path = files_path.replace("Results", "PCA_Results")
    if not os.path.isdir(PCA_path):
        os.makedirs(PCA_path)
    with open(PCA_path+'conversion_rates.json', 'w', encoding='utf-8') as f:
        json.dump(conversion_rates, f, ensure_ascii=False, indent=4)
        

    persian_labels = [get_display(reshape(label)) for label in conversion_rates.keys()]
    plt.bar(persian_labels, conversion_rates.values())
    plt.xticks(rotation=90, ha='right', fontsize = 8)
    plt.xlabel('District')
    plt.ylabel('Conversion Rate')
    plt.gca().yaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    plt.tight_layout()
    # plt.show()
    plt.savefig(PCA_path+"bar_plot.png")

compute_PCA_districts(files_path = "Results/apartment-rent/1/",
                      treshhold=100)


# hist, xedges, yedges = np.histogram2d(data_location['longitude'], data_location['latitude'], bins=20)
# x, y = np.meshgrid(xedges[:-1], yedges[:-1])
# coords = np.stack([x.ravel(), y.ravel()], axis=1)
# plt.imshow(hist.T, origin='lower', extent=[xedges[0], xedges[-1], yedges[0], yedges[-1]], cmap='viridis')
# plt.colorbar()
# plt.xlabel('longitude')
# plt.ylabel('latitude')
# plt.title('Heatmap of Credit and Rent Data')
# plt.show()