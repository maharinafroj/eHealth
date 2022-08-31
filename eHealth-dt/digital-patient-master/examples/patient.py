import os

import dgl
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
import numpy as np
import joblib

import digital_patient

from digital_patient.conformal.base import RegressorAdapter
from digital_patient.conformal.icp import IcpRegressor
from digital_patient.conformal.nc import RegressorNc
from examples.load_data import load_physiology
from examples.plot_graph import plot_graph


def main():
    result_dir = 'results/patient-old5/'
    if not os.path.isdir(result_dir):
        os.makedirs(result_dir)

    window_size = 500
    x_train, y_train, x_val, y_val, x_test, y_test, edge_list, addendum, scaler = load_physiology(window_size)
    joblib.dump(scaler, f'{result_dir}scaler.joblib')
  
    G = dgl.DGLGraph(edge_list)

    dp = digital_patient.DigitalPatient(G, epochs=20, lr=0.01, window_size=window_size-2)

    nx_G = dp.G.to_networkx()

    pos = nx.spring_layout(nx_G)
    node_labels = {}
    for i, cn in enumerate(list(addendum["RAS"][1]) + list(addendum["CARDIO"][1])):
        node_labels[i] = cn

    dp.fit(x_train, y_train)
    predictions = dp.predict(x_test)


    sns.set_style('whitegrid')
    for i, name in enumerate(list(addendum["RAS"][1]) + list(addendum["CARDIO"][1])):
        for j in range(predictions.shape[0]):
            xi = y_test[j, :, i]
            pi = predictions[j, :, i]

            if name == 't' or name == 't2':
                continue

            if name in addendum["RAS"][1]:
                ti = addendum["RAS"][0][j]
                ylabel= 'concentration [ng/mL]'
                xlabel = 't [days]'
            else:
                ti = addendum["CARDIO"][0][j]
                ylabel= 'pressure [mmHg]'
                xlabel = 't [sec]'

            tik = np.repeat(ti, pi.shape[0])
            pik = np.hstack(pi)

            df = pd.DataFrame(np.vstack([ti[np.newaxis, :], xi[np.newaxis, :], pi]).T)
            df.to_csv(f'{result_dir}/{name}_{j}.csv')

            plt.figure()
            plt.plot(ti, xi, label='true')
            for pik in pi:
                plt.plot(ti, pik, c='r', alpha=0.2)
        
            plt.title(name)
            plt.legend()
            plt.ylabel(ylabel)
            plt.xlabel(xlabel)
            plt.tight_layout()
            plt.savefig(f'{result_dir}/{name}_{j}.png')
            plt.show()
            break

    return


if __name__ == '__main__':
    main()
