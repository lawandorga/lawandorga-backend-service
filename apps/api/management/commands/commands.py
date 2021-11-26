from apps.api.management.commands.fixtures import Fixtures


def add_permissions():
    Fixtures.create_real_permissions_no_duplicates()
    Fixtures.create_real_folder_permissions_no_duplicate()
    Fixtures.create_real_collab_permissions()


def populate_deploy_db():
    Fixtures.create_real_origin_countries()
    add_permissions()
