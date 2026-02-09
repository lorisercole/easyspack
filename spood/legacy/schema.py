"""
JSON Schema definition for Spack spec configuration.
"""

SPEC_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Spack Spec Configuration",
    "description": "Schema for defining Spack specs and their dependencies to be added to a database",
    "type": "object",
    "required": ["software_target", "specs"],
    "properties": {
        "software_target": {
            "type": "string",
            "description": "Default architecture specification for all specs",
        },
        "specs": {
            "type": "array",
            "description": "List of spec configurations to add to the database",
            "minItems": 1,
            "items": {
                "$ref": "#/definitions/spec"
            }
        }
    },
    "definitions": {
        "spec": {
            "type": "object",
            "required": ["name", "version", "external_path"],
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Package name"
                },
                "version": {
                    "type": "string",
                    "description": "Package version"
                },
                "variants": {
                    "type": "string",
                    "description": "Spack variants specification (e.g., 'fabrics=ucx,psm')"
                },
                "explicit": {
                    "type": "boolean",
                    "description": "Whether to mark the spec as explicit in Spack",
                    "default": False
                },
                "external_path": {
                    "type": "string",
                    "description": "Path to external package installation"
                },
                "external_modules": {
                    "type": "array",
                    "description": "List of environment modules for this package",
                    "items": {
                        "type": "string"
                    }
                },
                "extra_attributes": {
                    "type": "object",
                    "description": "Additional attributes to set on the Spack spec",
                    "additionalProperties": True
                },
                "dependencies": {
                    "type": "array",
                    "description": "List of dependencies for this spec",
                    "items": {
                        "$ref": "#/definitions/dependency"
                    }
                }
            }
        },
        "dependency": {
            "type": "object",
            "required": ["name"],
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Name of the dependency package"
                },
                "depflags": {
                    "type": "array",
                    "description": "Dependency type flags",
                    "items": {
                        "type": "string",
                        "enum": ["BUILD", "LINK", "RUN", "TEST"]
                    },
                    "default": ["BUILD", "LINK"]
                },
                "virtuals": {
                    "type": "array",
                    "description": "Virtual package names this dependency provides",
                    "items": {
                        "type": "string"
                    },
                    "default": []
                }
            }
        }
    }
}
