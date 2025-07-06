class AnalysisRegistry:
    _analyses = {}

    @classmethod
    def register(
        cls,
        name,
        display_name,
        mem_attribute,
        csv_prefix,
        metric_fn,
        requires_min_time=False,
    ):
        cls._analyses[name] = {
            "display_name": display_name,
            "mem_attribute": mem_attribute,
            "csv_prefix": csv_prefix,
            "metric_fn": metric_fn,
            "requires_min_time": requires_min_time,
        }

    @classmethod
    def get_all(cls):
        if len(cls._analyses) == 0:
            raise RuntimeError(
                "Error, you must load analysis registers before proceed. Call register_all_analysis() to do that."
            )
        return cls._analyses
