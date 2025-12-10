#!/usr/bin/env python
"""
Entry point for UR3 actuator sizing and MJCF model generation.

Project layout:

  model-input/
    universalUR3.mjcf   # base UR3 MJCF (from MuJoCo "Save XML")
    universalUR3.urdf   # original URDF (not used directly here)

  model-output/
    ... generated MJCF models ...

Run from project root as:

  cd src
  python main.py
"""

from __future__ import annotations

from pathlib import Path

from sizing import HarmonicDrive, MotorShell, UR3ModelGenerator


def build_motor_config():
    """
    Define joint order, old motors (UR3) and new motors (harmonic drives).

    Old and new motors are specified here, in main, as requested.
    """
    joint_order = [
        "shoulder_pan_joint",
        "shoulder_lift_joint",
        "elbow_joint",
        "wrist_1_joint",
        "wrist_2_joint",
        "wrist_3_joint",
    ]

    # Old UR3 motors (approximate cylinders, in SI units)
    # Values taken from your OLD_MOTORS (base/shoulder/elbow/wrist1-3),
    # but remapped to joint names.
    old_motors: dict[str, MotorShell] = {
        "shoulder_pan_joint":  MotorShell(0.68, 17.5e-3, 12.9e-3),   # base motor
        "shoulder_lift_joint": MotorShell(0.68, 17.5e-3, 12.9e-3),   # shoulder motor
        "elbow_joint":         MotorShell(0.60, 15.5e-3, 10.65e-3),
        "wrist_1_joint":       MotorShell(0.33, 12.8e-3, 10.55e-3),
        "wrist_2_joint":       MotorShell(0.33, 12.8e-3, 10.55e-3),
        "wrist_3_joint":       MotorShell(0.33, 12.8e-3, 10.55e-3),
    }

    # New motors (your FHA-xxC-H data)
    NEW_WRIST = HarmonicDrive(
        name="FHA-25C-H",
        armature_inertia=3.2,   # kg·m^2 (GD^2/4 from catalog)
        mass=2.0,                # kg
        radius=0.047,            # m
        length=0.103,            # m
        max_torque=107.0,        # N·m
    )

    NEW_ELBOW = HarmonicDrive(
        name="FHA-32C-H",
        armature_inertia=7.1,    # kg·m^2
        mass=6.8,                # kg
        radius=0.057,            # m
        length=0.109,            # m
        max_torque=204.0,        # N·m
    )

    NEW_BASE = HarmonicDrive(
        name="FHA-40C-H",
        armature_inertia=10.8,    # kg·m^2
        mass=10.8,               # kg
        radius=0.230,            # m
        length=0.1438,            # m
        max_torque=686.0,        # N·m
    )

    # New motor choices per joint:
    # For shoulders: always NEW_BASE
    # For elbow:     NEW_ELBOW or NEW_BASE
    # For wrists:    NEW_WRIST or NEW_ELBOW
    new_motor_variants: dict[str, list[HarmonicDrive]] = {
        "shoulder_pan_joint":  [NEW_BASE],
        "shoulder_lift_joint": [NEW_BASE],
        "elbow_joint":         [NEW_ELBOW, NEW_BASE],
        "wrist_1_joint":       [NEW_WRIST, NEW_ELBOW],
        "wrist_2_joint":       [NEW_WRIST, NEW_ELBOW],
        "wrist_3_joint":       [NEW_WRIST, NEW_ELBOW],
    }

    return joint_order, old_motors, new_motor_variants


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]

    # Base MJCF produced by MuJoCo "File -> Save XML" from UR3 URDF
    base_mjcf = project_root / "model-input" / "universalUR3.xml"
    output_dir = project_root / "model-output"

    if not base_mjcf.exists():
        raise FileNotFoundError(f"Base MJCF not found: {base_mjcf}")

    joint_order, old_motors, new_motor_variants = build_motor_config()

    generator = UR3ModelGenerator(
        base_mjcf=base_mjcf,
        joint_order=joint_order,
        old_motors=old_motors,
        new_motor_variants=new_motor_variants,
        output_dir=output_dir,
    )

    # Single reference model (first motor choice per joint)
    baseline_path = generator.build_one_variant()

    # All combinations of NEW motors per joint
    generator.generate_all_variants()

    print(f"Done. Baseline model: {baseline_path}")


if __name__ == "__main__":
    # Run as:
    #   cd src
    #   python main.py
    main()
