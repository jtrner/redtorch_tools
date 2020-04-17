# Rigging code package

## Sourcing / Distribution of this package
Source-able and functional code within this library should be maintained in the following location:
`./src/iRig/...`

Importing code from this library is to follow one of the following namespace conventions:
- `from iRig.package import module`
- `import iRig.package.module`

Currently added to the `sys.path` through the `package.pth` file, these two paths are temporary 
and are intended to be removed as soon as re-targetting the import statements can allow:
- `./src/iRig/`
- `./src/iRig/iRig_maya/framework/`


## Future development suggestions:
- Rigging Framework:
    - Application-agnostic code relocate to: `./src/iRig/framework`
    - Application-specific code to live: `./src/iRig/app/framework`

- Application namespace:
    - Application-specific directories should be named by the application
        eg: `maya` / `houdini`
    - These directories will contain `__init__.py` file
    - The proposed import path experience will be:
        eg: `from iRig.maya.package import module`
