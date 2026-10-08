from pydantic import BaseModel, ConfigDict


class StrictModel(BaseModel):
    """Rejects unknown fields, at both validation and the JSON Schema we export.

    Without this, Pydantic's JSON Schema allows arbitrary extra properties,
    which makes json-schema-to-typescript emit a `[k: string]: unknown` index
    signature on every generated interface — defeating field-level typing on
    the frontend (e.g. `Omit<...>` collapses to the index signature).
    """

    model_config = ConfigDict(extra="forbid")
