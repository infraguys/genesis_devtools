# Versioning in Genesis Platform

This document describes the versioning strategy used in the Genesis Platform and
how it's implemented in the genesis_devtools package.

## Overview

The versioning system in Genesis Platform follows semantic versioning principles,
with additional enhancements for development and release candidate tracking.

## Version Format

Versions follow this format:

```text
MAJOR.MINOR.PATCH-RC/DEV+DATE.COMMITHEXSHA[:8]
```

## Examples

Release Version

```text
1.0.0
```

Development Version

```text
0.0.1-dev+20250618190326.a1beab7c
```

Release Candidate Version

```text
0.4.1-rc+20260220064549.9223faa6
```

## Use by genesis_devtools

```console
genesis get-version <ELEMENT_DIR>
```

Example

```console
user@user ~ → genesis get-version /home/user/PycharmProjects/genesis/restalchemy
15.0.5-dev+20260407054854.672dcc2c
```
