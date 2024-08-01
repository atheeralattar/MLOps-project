import mlflow
from mlflow import MlflowClient
from sklearn.metrics import mean_squared_error, r2_score
def mlflow_default_logging(model, model_tag, X_train, y_train, X_test, y_test):
    yp_train = model.predict(X_train)
    yp_test = model.predict(X_test)
        
    # Metrics
    rmse_train = mean_squared_error(y_train, yp_train, squared=False)
    rmse_valid = mean_squared_error(y_test, yp_test, squared=False)
    mlflow.set_tag("model", model_tag)
    r2=r2_score(y_test, yp_test)
    mlflow.log_metric("r2_test", r2)
    
def check_registry_if_not_exist(experiment):
    """ checks and creates a registry if not created
        and register the top run from that experiment
    Args:
        experiment_name (obj): experiment object
    """
    client = MlflowClient()
    registered_models_names = []
    registered_models = client.search_registered_models()
    for registred_model in registered_models:
        registered_models_names.append(registred_model.name)
    if experiment.name not in registered_models_names:
        mlflow.register_model()
        
def get_model_info(model_name, metric_name='r2_test'):
    """get the latest model version parameter

    Args:
        model_name (str): registered model name
        metric_name (str, optional): Defaults to 'r2_test'.

    Returns:
        parameter value
    """
    client = MlflowClient()
    try:
        # Get the latest version of the model
        latest_version = client.get_latest_versions(model_name, stages=["None"])[0]
        
        # Get the run ID associated with this model version
        run_id = latest_version.run_id
        
        # Fetch the run data
        run = client.get_run(run_id)
        
        # Extract the desired metric
        metric_value = run.data.metrics.get(metric_name)
        
        return {
            "model_name": model_name,
            "version": latest_version.version,
            "run_id": run_id,
            f"{metric_name}": metric_value
        }
    except Exception as e:
        print(f"Error getting info for model {model_name}: {str(e)}")
        return None


def pick_top_run(experiment: object, parameter):
    """ Picks the top run for a given experiment

    Args:
        experiment (obj): experiment object coming from search expirements
        parameter (str): parameter needed to sort the experiments according to

    Returns:
        top_run_id (str): run object from search run
    """
    client = MlflowClient()
    for run in client.search_runs(experiment.experiment_id):
        top_run = client.search_runs(
        experiment_ids=experiment.experiment_id,
        filter_string=f"metrics.{parameter} > 0",
        order_by=[f"metrics.{parameter} DESC"],
        max_results = 1    
        )
        
    return top_run[0].info.run_id
    
    
