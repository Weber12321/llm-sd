import typing as tp
from abc import ABC, abstractmethod
from dataclasses import make_dataclass, fields, asdict
import logging


def create_pipeline_input(fields: tp.Set[tp.Tuple]) -> tp.Type[tp.Any]:
    return make_dataclass("PipelineInput", fields)


class PipelineStep(ABC):
    @property
    @abstractmethod
    def input_class(self) -> type:
        pass

    @property
    @abstractmethod
    def output_class(self) -> type:
        pass

    @abstractmethod
    def execute(self, inputs: tp.Any) -> tp.Any:
        pass


class Pipeline:
    def __init__(self, **steps: PipelineStep):
        self.steps: tp.Dict[str, PipelineStep] = steps
        self.input_class = self._calculate_required_inputs()

    def __str__(self):
        step_info = []
        for step_name, step in self.steps.items():
            input_fields = [
                (field.name, getattr(field.type, "__name__", str(field.type)))
                for field in fields(step.input_class)
            ]
            output_fields = [
                (field.name, getattr(field.type, "__name__", str(field.type)))
                for field in fields(step.output_class)
            ]

            step_info.append(f"Step: {step_name}")
            step_info.append(
                f"  Input: {step.input_class.__name__} with fields: {input_fields}"
            )
            step_info.append(
                f"  Output: {step.output_class.__name__} with fields: {output_fields}"
            )
        return "Pipeline with steps:\n" + "\n".join(step_info)

    def __repr__(self):
        return self.__str__()

    def _calculate_required_inputs(self):
        inputs_needed = set()  # 所有步驟的必要輸入 (包含名稱和類型)
        outputs_produced = set()  # 步驟中自動產生的輸出 (只包含名稱)

        for step_name, step in self.steps.items():
            input_fields_with_type = {
                (field.name, field.type)
                for field in step.input_class.__dataclass_fields__.values()
            }

            input_field_names = {
                field.name
                for field in step.input_class.__dataclass_fields__.values()
            }
            output_field_names = {
                field.name
                for field in step.output_class.__dataclass_fields__.values()
            }

            missing_input_names = input_field_names - output_field_names
            missing_inputs = {
                field
                for field in input_fields_with_type
                if field[0] in missing_input_names
            }

            inputs_needed.update(missing_inputs)

            outputs_produced.update(output_field_names)

        return create_pipeline_input(inputs_needed)

    def get_input_params_info(self) -> tp.Set[str]:
        return [(field.name, field.type) for field in fields(self.input_class)]  # type: ignore

    def execute(self, **kwargs) -> dict:
        current_data = kwargs
        for step_name, step in self.steps.items():
            logging.info(f"Executing step: {step_name}")
            input_cls = step.input_class
            input_fields = {f.name for f in fields(input_cls)}
            step_inputs = {
                k: v for k, v in current_data.items() if k in input_fields
            }
            input_data = input_cls(**step_inputs)

            output_data = step.execute(input_data)

            current_data.update(asdict(output_data))
        return current_data
