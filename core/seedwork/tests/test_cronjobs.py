from core.seedwork.cronjobs import CronjobWarehouse


def test_warehouse(db):
    CronjobWarehouse.run_cronjobs()
