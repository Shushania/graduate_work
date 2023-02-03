def get_role_by_name(database, Model, name):
    role = (
        database.session
        .query(Model)
        .filter((Model.name == name))
        .first()
    )
    return role


def get_role_by_id(database, Model, model_id):
    role = (
        database.session
        .query(Model)
        .filter((Model.id == model_id))
        .first()
    )
    return role
