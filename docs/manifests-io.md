# Inputs and outputs of packages described by manifests

A manifest file represents an application package, more specifically its
imports, exports and permissions.

## Manifest

A manifest is made of an id/name, a version and targets.

A manifest may export:

- files using `file-properties`;
- plugins using `plugs`;
- permissions using `defined-permission`;
- bindings using `provided-binding`.

A manifest may import:

- permissions using `required-permission`.

## Targets

A target is made of an id (`target`)/name and some content.

A target may export:

- APIs using `provided-api`.

A target may import/use:

- configuration using `required-config`
- APIs using `required-api`
- bindings using `required-binding`
- permissions using `required-permission`
- systemd unit using `required-systemd`
