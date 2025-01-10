from ..base_pipe import Pipeline


def get_txt_pipeline() -> Pipeline:
    from ..loader.txt_loader import TxtLoader

    loader = TxtLoader()
    pipeline = Pipeline(load=loader)
    return pipeline
