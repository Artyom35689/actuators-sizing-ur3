# UR3 Actuator Sizing and MJCF Model Generation

This repository contains a small utility to generate MuJoCo MJCF models of the UR3 robot with alternative actuators.  
The script replaces the original UR motors with FHA-C hollow-shaft rotary actuators, updates link inertias, sets joint armature values, and creates torque-limited MuJoCo actuators.

## References

- FHA-C hollow-shaft servo actuators (motor masses, dimensions, inertia, torques):  
  https://www.harmonicdrive.net/products/rotary-actuators/hollow-shaft-servo-actuators/fha-c

- UR3 max joint torques (for actuator selection and sanity checks):  
  https://www.universal-robots.com/articles/ur/robot-care-maintenance/max-joint-torques-cb3-and-e-series/

## Project structure

```text
.
├── LICENSE
├── model-input
│   ├── universalUR3.mjcf   # base UR3 MJCF ("File → Save XML" from URDF in MuJoCo)
│   └── universalUR3.urdf   # original URDF (reference)
├── model-output            # generated MJCF models (output)
├── README.md
└── src
    ├── main.py             # CLI entry point, motor config, runs generation
    └── sizing.py           # inertial math and MJCF manipulation utilities
````

## Dependencies

* Python 3.10+ (tested with CPython)
* [NumPy](https://numpy.org/)
* [lxml](https://lxml.de/) (for XML / MJCF manipulation)

Optional, for visualizing the resulting models:

* [MuJoCo](https://mujoco.readthedocs.io/) 3.x (or newer)
* MuJoCo Python bindings if you want to simulate from Python

Install (example):

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install numpy lxml
```

## Usage

1. Place the base UR3 MJCF file as:

   ```text
   model-input/universalUR3.xml
   ```

   This file should be obtained by loading the UR3 URDF into MuJoCo and using
   **File → Save XML**.

2. Run the generator:

   ```bash
   cd src
   python main.py
   ```

3. Outputs:

   * A baseline model with one fixed actuator choice per joint:

     * `model-output/ur3_new_replace_motor_single.xml`
   * A set of models for all combinations of configured actuators:

     * `model-output/ur3_new_variant_XX.xml`

The motor data (masses, dimensions, armature inertia, torque limits) are defined in `src/main.py` and can be edited there if you want to try different actuator configurations.

