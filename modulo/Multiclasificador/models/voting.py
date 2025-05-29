import joblib
import pandas as pd
from sklearn.ensemble import VotingClassifier
from sklearn.model_selection import cross_val_score
from modulo.Multiclasificador.utils import utils


def build_voting_models(subsets, data_path):
    data = utils.loadData(data_path)
    n_columns = data.shape[1]
    x_instances = data[:, :n_columns - 1]
    y_instances = data[:, -1]

    source_folder = 'modulo/Multiclasificador/voting/models_and_evaluation'
    name_evaluation_file = source_folder + '/evaluacion.txt'
    folders = source_folder + '/models'
    utils.create_folder(folders)

    metricas = ['accuracy', 'precision', 'recall', 'f1', 'roc_auc']
    model_id = []
    performance = []
    for i in range(len(subsets)):
        performance.append([])

    utils.create_folder(folders)
    for i, subset in enumerate(subsets):
        number = 1 + i
        model_id.append('Vot-' + str(number))
        name_model_file = folders + '/Vot-' + str(number) + '.pickle'

        vote = VotingClassifier(estimators=subset, voting='soft', flatten_transform=False, n_jobs=-1)
        for metrica in metricas:
            scoring = cross_val_score(vote, x_instances, y_instances, scoring=metrica, cv=5)
            performance[i].append(round(scoring.mean(), 2))

        model = vote.fit(x_instances, y_instances)
        joblib.dump(model, r'' + name_model_file)
    print("Modelos Voting construídos")
    results = pd.DataFrame(performance, columns=metricas, index=model_id)

    with open(name_evaluation_file, 'w') as f:
        utils.create_txt_report(results, subsets, f)

    # name_graph = source_folder + '/voting_barplot.png'
    # title = 'Evaluación del multiclasificador Voting'
    # xlabel = 'Subconjunto de clasificadores'
    # ylabel = 'Valor de las métricas'
    # utils.plot_results(results, name_graph, title, xlabel, ylabel)
