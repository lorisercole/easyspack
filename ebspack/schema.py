"""
JSON Schema definition for Spack spec configuration.
"""

SPEC_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Spack Spec Configuration",
    "description": "Schema for defining Spack specs and their dependencies to be added to a database",
    "type": "object",
    "required": ["architecture", "specs"],
    "properties": {
        "architecture": {
            "type": "object",
            "description": "Default architecture specification for all specs",
            "required": ["platform", "os", "target"],
            "properties": {
                "platform": {
                    "type": "string",
                    "description": "Platform name (e.g., 'linux', 'darwin', 'windows')"
                },
                "os": {
                    "type": "string",
                    "description": "Operating system name (e.g., 'ubuntu24.04', 'centos7')"
                },
                "target": {
                    "type": "string",
                    "description": "Target architecture (e.g., 'skylake', 'x86_64', 'aarch64')"
                }
            }
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
            "required": ["name", "version"],
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
                "architecture": {
                    "type": "object",
                    "description": "Override default architecture for this spec",
                    "required": ["platform", "os", "target"],
                    "properties": {
                        "platform": {"type": "string"},
                        "os": {"type": "string"},
                        "target": {"type": "string"}
                    }
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
