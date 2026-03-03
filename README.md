# Real Spherical Harmonics OBJ Exporter

A Python tool for generating 3D mesh files (.obj) of real spherical harmonics and their linear combinations. The meshes are colored by the sign of harmonic values with customizable colors.

## Features

- Export individual real spherical harmonics Y_l^m as 3D meshes
- Create linear combinations (superpositions) of spherical harmonics
- Customizable vertex coloring (select colors for positive and negative values)
- Adjustable mesh resolution

## Installation

1. Clone or download this repository
2. Create a virtual environment (recommended):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Make the script executable (optional, Unix/macOS):
   ```bash
   chmod +x realspherical.py
   ```

## Usage

### Command Line Interface

Export a single spherical harmonic:
```bash
python realspherical.py --single 2 0 --output Y_2_0.obj
```

Export multiple harmonics at once:
```bash
python realspherical.py --single 2 0 --single 3 -2 --single 3 2
```

Export a linear combination:
```bash
python realspherical.py --combo "3,-3,0.5" "3,-2,0.3" "3,0,0.7" --output superposition.obj
```

Adjust mesh resolution (default is 100x100):
```bash
python realspherical.py --single 2 0 --resolution 200
```

Customize colors (use RGB values 0-1 or 0-255):
```bash
# Green for positive, magenta for negative (0-1 format)
python realspherical.py --single 3 0 --color-positive "0,1,0" --color-negative "1,0,1"

# Orange for positive, purple for negative (0-255 format)
python realspherical.py --single 2 2 --cp "255,165,0" --cn "128,0,128"
```

Run examples from the script:
```bash
python realspherical.py --examples
```

### Python API

```python
from realspherical import export_spherical_harmonic, export_superposition

# Export a single spherical harmonic (default red/blue colors)
export_spherical_harmonic(l=2, m=0, filename="Y_2_0.obj")

# Export with custom colors
export_spherical_harmonic(
    l=3, m=2, 
    filename="Y_3_2.obj",
    color_positive=(0.0, 1.0, 0.0),  # Green for positive
    color_negative=(1.0, 0.0, 1.0)   # Magenta for negative
)

# Export a linear combination
factors = [
    (3, -3, 0.5),  # l=3, m=-3, coefficient=0.5
    (3, -2, 0.3),  # l=3, m=-2, coefficient=0.3
    (3,  0, 0.7),  # l=3, m=0,  coefficient=0.7
]
export_superposition(
    factors, 
    filename="combo.obj",
    color_positive=(1.0, 0.65, 0.0),  # Orange
    color_negative=(0.5, 0.0, 0.5)    # Purple
)
```

## Colors

The meshes are colored based on the sign of the spherical harmonic values at each vertex:
- **Positive values**: Default is red `(1.0, 0.0, 0.0)`, customizable
- **Negative values**: Default is blue `(0.0, 0.0, 1.0)`, customizable

### Specifying Custom Colors

Colors can be specified in two formats:
- **0-1 format**: `"R,G,B"` where each value is between 0 and 1
  - Example: `"0,1,0"` for pure green
- **0-255 format**: `"R,G,B"` where each value is between 0 and 255
  - Example: `"255,165,0"` for orange

The script automatically detects which format you're using.

### Common Colors

| Color | 0-1 Format | 0-255 Format |
|-------|-----------|--------------|
| Red | `1,0,0` | `255,0,0` |
| Green | `0,1,0` | `0,255,0` |
| Blue | `0,0,1` | `0,0,255` |
| Yellow | `1,1,0` | `255,255,0` |
| Magenta | `1,0,1` | `255,0,255` |
| Cyan | `0,1,1` | `0,255,255` |
| Orange | `1,0.65,0` | `255,165,0` |
| Purple | `0.5,0,0.5` | `128,0,128` |
| White | `1,1,1` | `255,255,255` |
| Black | `0,0,0` | `0,0,0` |

## Parameters

- **l**: Degree of the spherical harmonic (non-negative integer)
- **m**: Order of the spherical harmonic (integer, -l ≤ m ≤ l)
- **n_theta**: Number of grid points in polar direction (default: 100)
- **n_phi**: Number of grid points in azimuthal direction (default: 100)
- **color_positive**: RGB color tuple for positive values (default: red)
- **color_negative**: RGB color tuple for negative values (default: blue)

## Examples

The script includes built-in examples that demonstrate:
- Individual spherical harmonics (Y_2^0, Y_3^-2)
- F-orbital-like shapes from linear combinations of l=3 harmonics

Run them with:
```bash
python realspherical.py --examples
```

## Output

All OBJ files are exported to the `output/` directory by default. The meshes can be viewed in any 3D software that supports OBJ format (e.g., Blender).

## Mathematical Background

Real spherical harmonics are derived from complex spherical harmonics:
- For m = 0: Y_l^0 = Y_l^0 (real part)
- For m > 0: Y_l^m = √2 · (-1)^m · Re(Y_l^m)
- For m < 0: Y_l^m = √2 · (-1)^m · Im(Y_l^|m|)

The mesh radius at each point is scaled by |Y_l^m|, creating the characteristic lobe patterns.