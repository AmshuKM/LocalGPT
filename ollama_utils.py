from ollama import list


def get_models():

    response = list()

    models = []

    for model in response.models:

        models.append(model.model)

    return models